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

## Deliberate Exclusions

- The canonical unit-test command and discovery contract belong to task `0005`.
- Migration content and storage package wiring belong to later storage tasks.
- Observability keeps the standard-library logging baseline for now and does not add a dedicated logging or metrics package in this task.
