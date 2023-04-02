"""Session object"""
from __future__ import annotations

import logging
import os
from types import TracebackType
from typing import Iterable, List, Optional, Type
from uuid import UUID

from cachetools import TTLCache, cached
from httpx import ConnectError
from notion_client.errors import APIResponseError
from notional import blocks, types
from notional.session import Session as NotionalSession

from .database import Database
from .page import Page
from .user import User
from .utils import ObjRef, SList, make_obj_ref

_log = logging.getLogger(__name__)
ENV_NOTION_AUTH_TOKEN = "NOTION_AUTH_TOKEN"


class SessionError(Exception):
    """Raised when there are issues with the Notion session."""

    def __init__(self, message):
        """Initialize the `NotionSessionError` with a supplied message."""
        super().__init__(message)


class Session(object):
    """A session for the Notion API"""

    def __init__(self, auth: Optional[str] = None, **kwargs):
        """Initialize the `Session` object and the Notional endpoints.

        Args:
            auth: secret token from the Notion integration
            **kwargs: Arguments for the [Notion SDK Client][https://ramnes.github.io/notion-sdk-py/reference/client/]
        """
        if auth is None:
            if (env_token := os.getenv(ENV_NOTION_AUTH_TOKEN)) is not None:
                auth = env_token
            else:
                raise RuntimeError(f"Either pass `auth` or set {ENV_NOTION_AUTH_TOKEN}")

        self.notional = NotionalSession(auth=auth, **kwargs)

        # prepare API methods for decoration
        self._search_db_unwrapped = self.search_db
        self._get_db_unwrapped = self._get_db
        self._get_page_unwrapped = self._get_page
        self._get_user_unwrapped = self._get_user
        self.set_cache()
        _log.info("Initialized Notion session")

    def set_cache(self, ttl=30, maxsize=1024):
        wrapper = cached(cache=TTLCache(maxsize=maxsize, ttl=ttl))
        self.search_db = wrapper(self._search_db_unwrapped)
        self._get_db = wrapper(self._get_db_unwrapped)
        self._get_page = wrapper(self._get_page_unwrapped)
        self._get_user = wrapper(self._get_user_unwrapped)

    def __enter__(self) -> Session:
        _log.debug("Connecting to Notion...")
        self.notional.client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        _log.debug("Closing connection to Notion...")
        self.notional.client.__exit__(exc_type, exc_value, traceback)

    def close(self):
        """Close the session and release resources."""
        self.notional.client.close()

    def raise_for_status(self):
        """Confirm that the session is active and raise otherwise.

        Raises SessionError if there is a problem, otherwise returns None.
        """
        error = None

        try:
            me = self.whoami()

            if me is None:
                raise SessionError("Unable to get current user")
        except ConnectError:
            error = "Unable to connect to Notion"
        except APIResponseError as err:
            error = str(err)

        if error is not None:
            raise SessionError(error)

    def search_db(
        self, db_name: Optional[str] = None, exact: bool = True, parents: Optional[Iterable[str]] = None
    ) -> SList[Database]:
        """Search a database by name

        Args:
            db_name: name/title of the database, return all if `None`
            exact: perform an exact search, not only a substring match
            parents: list of parent pages to further refine the search
        """
        if parents is not None:
            # ToDo: Implement a search that also considers the parents
            raise NotImplementedError

        query = self.notional.search(db_name).filter(property="object", value="database")
        dbs = SList(Database(db_block=db, session=self) for db in query.execute())
        if exact and db_name is not None:
            dbs = SList(db for db in dbs if db.title == db_name)
        return dbs

    def _get_db(self, uuid: UUID) -> blocks.Database:
        """Retrieve Notional database block by uuid

        This indirection is needed since more general object references are not hashable.
        """
        return self.notional.databases.retrieve(uuid)

    def get_db(self, db_ref: ObjRef) -> Database:
        db_uuid = make_obj_ref(db_ref).id
        return Database(db_block=self._get_db(db_uuid), session=self)

    def _search_page(self):
        raise NotImplementedError

    def search_page(
        self, page_name: Optional[str] = None, exact: bool = True, parents: Optional[Iterable[str]] = None
    ) -> SList[Page]:
        raise NotImplementedError

    def _get_page(self, uuid: UUID) -> blocks.Page:
        """Retrieve Notional page by uuid

        This indirection is needed since more general object references are not hashable.
        """
        return self.notional.pages.retrieve(uuid)

    def get_page(self, page_ref: ObjRef) -> Page:
        page_uuid = make_obj_ref(page_ref).id
        return Page(obj_ref=self._get_page(page_uuid), session=self)

    def _get_user(self, uuid: UUID) -> types.User:
        return self.notional.users.retrieve(uuid)

    def get_user(self, user_ref: ObjRef) -> User:
        user_uuid = make_obj_ref(user_ref).id
        return User(obj_ref=self.notional.users.retrieve(user_uuid))

    def whoami(self) -> User:
        """Return the user object of this bot"""
        return self.notional.users.me()

    def all_users(self) -> List[User]:
        """Retrieve all users of this workspace"""
        return [User(obj_ref=user) for user in self.notional.users.list()]
