# Dependency Baseline

`requirements.txt` is the canonical dependency surface for M0 local setup and Docker builds.

## Covered Baseline

The pinned baseline covers one shared install surface for:

- Telegram runtime transport via `telethon`
- Environment loading via `python-dotenv`
- YAML configuration parsing via `PyYAML`
- PostgreSQL access via `asyncpg`
- SQLAlchemy async Core storage integration via `SQLAlchemy`
- Schema migrations via `alembic`
- Unit-test dependency installation and async test support via `pytest` and `pytest-asyncio`

## Installation Contract

- Local setup installs dependencies with `python -m pip install -r requirements.txt`.
- Docker builds install the same `requirements.txt` file.
- M0 does not support a second dependency-install mechanism such as `pyproject.toml`, `requirements-dev.txt`, or `requirements-test.txt`.

## Unit-Test Contract

- The canonical M0 unit-test command is `python -m pytest` from the repository root.
- Repo-tracked unit tests are discovered from `tests/unit/`.
- The test runner resolves `telegram_aggregator` imports from `src/` via repo-tracked `pytest` configuration rather than an installable package workflow.
- Async unit tests use `pytest-asyncio` in `strict` mode: async tests must declare `@pytest.mark.asyncio`, and async fixtures must use `@pytest_asyncio.fixture`.

## Deliberate Exclusions

- Migration content and storage package wiring belong to later storage tasks.
- Observability keeps the standard-library logging baseline for now and does not add a dedicated logging or metrics package in this task.
