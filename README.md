<div align="center">
<img src="https://raw.githubusercontent.com/ultimate-notion/ultimate-notion/master/docs/assets/images/logo_with_text.svg" alt="Ultimate-Notion logo" width="500" role="img">
</div>
<br/>

Ultimate Notion is the ultimate Python library for [Notion]! It allows you to access and modify your Notion databases and
pages in the most convenient and pythonic way.

|         |                                    |
|---------|------------------------------------|
| CI/CD   | [![Tests][Tests-image]][Tests-link] [![Coverage][Coverage-image]][Coverage-link] [![Publish Package][Publish-image]][Publish-link] [![Build Docs][Docs-image]][Docs-link] |
| Package | [![PyPI - Version][PyPI_ver-image]][PyPI_ver-link] [![PyPI - Downloads][PyPI_down-image]][PyPI_down-link] [![PyPI - Python Version][PyPI_py-image]][PyPI_py-link] |
| Details | [![Hatch project][hatch-image]][hatch-link] [![linting - Ruff][ruff-image]][ruff-link] [![code style - black][black-image]][black-link] [![types - Mypy][mypy-image]][mypy-link] [![License - MIT][MIT-image]][MIT-link] [![GitHub Sponsors][sponsor-image]][sponsor-link] |



**This is a pre-alpha version! Don't use it!**

## Development

After having cloned this repository:

1. make sure [hatch] in installed globally, e.g. `pipx install hatch`,
2. optionally run `hatch config set dirs.env.virtual .direnv` to let [VS Code] find your virtual environments,
3. make sure `pre-commit` is installed globally, e.g. with `pipx install pre-commit`,

and then you are already set up to start hacking. Use `hatch run cov` or `hatch run no-cov` to run
the unitest with or without coverage reports, respectively. Check out the environment setup of
hatch in [pyproject.toml](pyproject.toml) for many more commands.

If you are using [VS Code], then it's quite convenient to add a file `.env` in your checkout with:

```ini
[pytest]
env =
    NOTION_AUTH_TOKEN=secret_YOUR_TOKEN_TO_YOUR_TEST_NOTION_ACCOUNT
```

## Documentation

The [Ultimate Notion documentation] is made with [Material for MkDocs] and is hosted on [GitHub Pages].

## License

Ultimate Notion is distributed under the terms of the [MIT license](LICENSE.txt).

## Credits

To start this project off a lot of inspiration and code was taken from [hatch] and [notional].
Ultimate Notion uses internally [notion-sdk-py].

[Notion]: https://www.notion.so/
[hatch]: https://hatch.pypa.io/
[pre-commit]: https://pre-commit.com/
[notional]: https://github.com/jheddings/notional/
[notion-sdk-py]: https://github.com/ramnes/notion-sdk-py/
[Material for MkDocs]: https://github.com/squidfunk/mkdocs-material
[GitHub Pages]: https://docs.github.com/en/pages
[Ultimate Notion documentation]: https://ultimate-notion.com/
[VS Code]: https://code.visualstudio.com/

[Tests-image]: https://github.com/ultimate-notion/ultimate-notion/actions/workflows/run-tests.yml/badge.svg
[Tests-link]: https://github.com/ultimate-notion/ultimate-notion/actions/workflows/run-tests.yml
[Coverage-image]: https://img.shields.io/coveralls/github/ultimate-notion/ultimate-notion/master.svg?logo=coveralls&label=Coverage
[Coverage-link]: https://coveralls.io/r/ultimate-notion/ultimate-notion
[Publish-image]: https://github.com/ultimate-notion/ultimate-notion/actions/workflows/publish-pkg.yml/badge.svg
[Publish-link]: https://github.com/ultimate-notion/ultimate-notion/actions/workflows/publish-pkg.yml
[Docs-image]: https://github.com/ultimate-notion/ultimate-notion/actions/workflows/build-dev-docs.yml/badge.svg
[Docs-link]: https://github.com/ultimate-notion/ultimate-notion/actions/workflows/build-dev-docs.yml
[PyPI_ver-image]: https://img.shields.io/pypi/v/ultimate-notion.svg?logo=pypi&label=PyPI&logoColor=gold
[PyPI_ver-link]: https://pypi.org/project/ultimate-notion/
[PyPI_down-image]: https://img.shields.io/pypi/dm/ultimate-notion.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold
[PyPI_down-link]: https://pepy.tech/project/ultimate-notion
[PyPI_py-image]: https://img.shields.io/pypi/pyversions/ultimate-notion.svg?logo=python&label=Python&logoColor=gold
[PyPI_py-link]: https://pypi.org/project/ultimate-notion/
[hatch-image]: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
[hatch-link]: https://github.com/pypa/hatch
[ruff-image]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[ruff-link]: https://github.com/charliermarsh/ruff
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/psf/black
[mypy-image]: https://img.shields.io/badge/types-Mypy-blue.svg
[mypy-link]: https://mypy-lang.org/
[MIT-image]: https://img.shields.io/badge/license-MIT-9400d3.svg
[MIT-link]: LICENSE.txt
[sponsor-image]: https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=ff69b4
[sponsor-link]: https://github.com/sponsors/FlorianWilhelm
