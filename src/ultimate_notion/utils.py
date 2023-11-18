"""Additional utilities that fit nowhere else"""

from __future__ import annotations

from copy import deepcopy
from functools import wraps
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeAlias, TypeVar, cast
from uuid import UUID

import numpy as np

from ultimate_notion.obj_api import objects as objs
from ultimate_notion.obj_api.core import GenericObject

if TYPE_CHECKING:
    from ultimate_notion.session import Session


ObjRef: TypeAlias = UUID | str


T = TypeVar('T')


class SList(list[T]):
    """A list that holds often only a single element"""

    def item(self) -> T:
        if len(self) == 1:
            return self[0]
        elif len(self) == 0:
            msg = 'list is empty'
        else:
            msg = f"list of '{type(self[0]).__name__}' objects has more than one element"
        raise ValueError(msg)


def is_notebook() -> bool:
    """Determine if we are running within a Jupyter notebook"""
    try:
        from IPython import get_ipython  # noqa: PLC0415
    except ModuleNotFoundError:
        return False  # Probably standard Python interpreter
    else:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)


def store_retvals(func):
    """Decorator storing the return values as function attribute for later cleanups

    This can be used for instance in a generator like this:
    ```
    @pytest.fixture
    def create_blank_db(notion, test_area):
        @store_retvals
        def nested_func(db_name):
            db = notion.databases.create(
                parent=test_area,
                title=db_name,
                schema={
                    "Name": schema.Title(),
                },
            )
            return db

        yield nested_func

        # clean up by deleting the db of each prior call
        for db in nested_func.retvals:
            notion.databases.delete(db)
    ```
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        retval = func(*args, **kwargs)
        wrapped.retvals.append(retval)
        return retval

    wrapped.retvals = []
    return wrapped


def find_indices(elements: np.ndarray | list[Any], total_set: np.ndarray | list[Any]) -> np.array:
    """Finds the indices of the elements in the total set"""
    if not isinstance(total_set, np.ndarray):
        total_set = np.array(total_set)
    mask = np.isin(total_set, elements)
    indices = np.where(mask)[0]
    lookup = dict(zip(total_set[mask], indices, strict=True))
    result = np.array([lookup.get(x, None) for x in elements])
    return result


def find_index(elem: Any, lst: list[Any]) -> int | None:
    """Find the index of the element in the list or return `None`"""
    if elem not in lst:
        return None
    else:
        return lst.index(elem)


def deepcopy_with_sharing(obj: Any, shared_attributes: list[str], memo: dict[int, Any] | None = None):
    """
    Deepcopy an object, except for a given list of attributes, which should
    be shared between the original object and its copy.

    Args:
        obj: some object to copy
        shared_attributes: A list of strings identifying the attributes that should be shared instead of copied.
        memo: dictionary passed into __deepcopy__.  Ignore this argument if not calling from within __deepcopy__.

    Example:
        ```python
        class A(object):
            def __init__(self):
                self.copy_me = []
                self.share_me = []

            def __deepcopy__(self, memo):
                return deepcopy_with_sharing(
                    self, shared_attribute_names=["share_me"], memo=memo
                )


        a = A()
        b = deepcopy(a)
        assert a.copy_me is not b.copy_me
        assert a.share_me is b.share_me

        c = deepcopy(b)
        assert c.copy_me is not b.copy_me
        assert c.share_me is b.share_me
        ```

    Original from https://stackoverflow.com/a/24621200
    """
    shared_attrs = {k: getattr(obj, k) for k in shared_attributes}

    deepcopy_defined = hasattr(obj, '__deepcopy__')
    if deepcopy_defined:
        # Do hack to prevent infinite recursion in call to deepcopy
        deepcopy_method = obj.__deepcopy__
        obj.__deepcopy__ = None

    for attr in shared_attributes:
        del obj.__dict__[attr]

    clone = deepcopy(obj, memo)

    for attr, val in shared_attrs.items():
        setattr(obj, attr, val)
        setattr(clone, attr, val)

    if deepcopy_defined:
        # Undo hack
        obj.__deepcopy__ = deepcopy_method
        del clone.__deepcopy__

    return clone


def get_uuid(obj: str | UUID | objs.ParentRef | objs.NotionObject) -> UUID:
    """Retrieves a UUID from an object reference using Notional

    Only meant for internal use.
    """
    return objs.ObjectReference.build(obj).id


KT = TypeVar('KT')
VT = TypeVar('VT')


def dict_diff(dct1: dict[KT, VT], dct2: dict[KT, VT]) -> tuple[list[KT], list[KT], dict[KT, tuple[VT, VT]]]:
    """Returns the added keys, removed keys and keys of changed values of both dictionaries"""
    set1, set2 = set(dct1.keys()), set(dct2.keys())
    keys_added = list(set2 - set1)
    keys_removed = list(set1 - set2)
    values_changed = {key: (dct1[key], dct2[key]) for key in set1 & set2 if dct1[key] != dct2[key]}
    return keys_added, keys_removed, values_changed


def dict_diff_str(dct1: dict[KT, VT], dct2: dict[KT, VT]) -> tuple[str, str, str]:
    """Returns the added keys, removed keys and keys of changed values of both dictionaries as strings for printing"""
    keys_added, keys_removed, values_changed = dict_diff(dct1, dct2)
    keys_added_str = ', '.join([str(k) for k in keys_added]) or 'None'
    keys_removed_str = ', '.join([str(k) for k in keys_removed]) or 'None'
    keys_changed_str = ', '.join(f'{k}: {v[0]} -> {v[1]}' for k, v in values_changed.items()) or 'None'
    return keys_added_str, keys_removed_str, keys_changed_str


Self = TypeVar('Self', bound='Wrapper[Any]')  # ToDo: Replace when requires-python >= 3.11
GT = TypeVar('GT', bound=GenericObject)  # ToDo: Use new syntax when requires-python >= 3.12


class Wrapper(Generic[GT]):
    """Convert objects from the obj-based API to the high-level API and vice versa"""

    obj_ref: GT

    _obj_api_map: ClassVar[dict[type[GT], type[Wrapper]]] = {}  # type: ignore[misc]

    def __init_subclass__(cls, wraps: type[GT], **kwargs: Any):
        super().__init_subclass__(**kwargs)
        cls._obj_api_map[wraps] = cls

    def __new__(cls: type[Wrapper], *args, **kwargs) -> Wrapper:
        # Needed for wrap_obj_ref and its call to __new__ to work!
        return super().__new__(cls)

    def __init__(self, *args: Any, **kwargs: Any):
        """Default constructor that also builds `obj_ref`"""
        obj_api_type: type[GenericObject] = self._obj_api_map_inv[self.__class__]
        self.obj_ref = obj_api_type.build(*args, **kwargs)

    @classmethod
    def wrap_obj_ref(cls: type[Self], obj_ref: GT, /) -> Self:
        """Wraps `obj_ref` into a high-level object for the API of Ultimate Notion"""
        hl_cls = cls._obj_api_map[type(obj_ref)]
        hl_obj = hl_cls.__new__(hl_cls)
        hl_obj.obj_ref = obj_ref
        return cast(Self, hl_obj)

    @property
    def _obj_api_map_inv(self) -> dict[type[Wrapper], type[GT]]:
        return {v: k for k, v in self._obj_api_map.items()}


def get_active_session() -> Session:
    """Return the current active session or raise an exception

    Avoids cyclic imports when used within the package itself.
    For internal use mostly.
    """
    from ultimate_notion.session import Session  # noqa: PLC0415

    return Session.get_active()


def get_repr(obj: Any, /, *, name: Any = None, desc: Any = None) -> str:
    """Default representation, i.e. `repr(...)`, used by ultime-notion for conistency"""
    type_str = str(name) if name is not None else obj.__class__.__name__
    desc_str = str(desc) if desc is not None else str(obj)
    return f"<{type_str}: '{desc_str}' at {hex(id(obj))}>"
