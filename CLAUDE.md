# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Telegram-ggregator is a Python async service that reads Telegram source channels via a user session (Telethon/MTProto), filters and deduplicates messages, and publishes selected events to a target channel. Postgres stores message, candidate, and event state.

## Commands

### Run service (Docker Compose)
```bash
docker compose up app
```

### Run login (interactive Telegram auth)
```bash
docker compose run --rm app python -m telegram_aggregator.login
```

### Run tests
```bash
pytest                          # all unit tests
pytest tests/unit/config/       # single directory
pytest tests/unit/config/test_app_config.py::test_name  # single test
```

### Install local deps (for tests/tooling only)
```bash
python -m pip install -r requirements.txt
```

### Build container
```bash
docker compose build app
```

## Architecture

Single async Python service. Canonical package: `src/telegram_aggregator/`.

**Entry points:**
- `python -m telegram_aggregator` → `__main__.py` → `bootstrap.service.run_service()`
- `python -m telegram_aggregator.login` → `login.py` → `bootstrap.login.run_login()`

**Key packages under `src/telegram_aggregator/`:**
- `bootstrap/` — Service and login initialization, runtime wiring
- `config/` — Env-based (`app_config.py`) + YAML-based (`file_config.py`) config loading, semantic validation
- `telegram/` — Telethon client abstraction, error types
- `processing/` — In-process message queue and filtering pipeline

**Pipeline flow:** Telethon event → message reader → processing queue → candidate aggregation → publish queue → target channel

**Configuration:** Environment variables for secrets/runtime (see `.env.example`), YAML file for sources/filters/runtime tuning (see `config.example.yaml`). `DRY_RUN=1` disables all Telegram I/O.

## Testing

- Framework: pytest + pytest-asyncio (strict mode)
- All tests in `tests/unit/`, pythonpath set to `src/`
- `conftest.py` provides `FakeTelethonClient`, env setup fixtures, and YAML config fixtures
- Import mode: importlib

## Conventions

- Write code comments and documentation in English
- Address the user in Ukrainian by default
- Prefer simple solutions over clever ones
- Preserve existing behavior unless the task requires a change
- Canonical package root is `src/telegram_aggregator/` (ignore any `src/Telegram-aggregator/` legacy scaffold)
- Planning tasks referenced by number (e.g. `0009`) can be resolved via `bin/find-planning-item 0009` or by searching `docs/planning/active/` then `docs/planning/archive/`
- Project knowledge and architecture docs live under `docs/` — start with `docs/project/overview.md` and `docs/project/architecture.md`
