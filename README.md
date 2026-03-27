# Telegram-ggregator

Telegram-ggregator is a Python service repository in its initial setup stage.

Project knowledge, planning documents, and role definitions live under [docs/README.md](docs/README.md).

## Run Contract

The supported local startup contract is containerized through Docker Compose.

Copy the example environment file before running the service.

```bash
cp .env.example .env
```

For the supported Compose path, keep `TG_SESSION_PATH=/var/app/sessions/default.session` and `CONFIG_PATH=/var/app/config.example.yaml`. The `app` service uses the repository bind mount, so both paths resolve to repository files on the host.

The application runtime contract is `TG_API_ID`, `TG_API_HASH`, `TG_SESSION_PATH`, `DATABASE_URL`, `TARGET_CHANNEL`, `CONFIG_PATH`, `LOG_LEVEL`, and `DRY_RUN`.
`TG_API_ID`, `TG_API_HASH`, and `TARGET_CHANNEL` may be left blank only while `DRY_RUN=1`.
`POSTGRES_*` values in `.env` are only for the local Compose `postgres` service.

The login command prompts for the phone number, login code, and 2FA password interactively when Telegram requires them.
They are not part of the canonical environment contract.

`DRY_RUN=1` disables all Telegram network I/O.
Use it only for non-Telegram bootstrap and local verification paths.
The checked-in `.env.example` is a dry-run bootstrap profile. Before using Telegram-backed startup or `python -m telegram_aggregator.login`, switch to `DRY_RUN=0` and fill the Telegram-facing values.

Install Python dependencies locally only when you need repository tooling such as tests.

```bash
python -m pip install -r requirements.txt
```

Start the service locally through Compose.

```bash
docker compose up app
```

Run the canonical login entrypoint through the same container image.

```bash
docker compose run --rm app python -m telegram_aggregator.login
```

Apply database migrations before the first run or after pulling new revisions.

```bash
docker compose run --rm app alembic upgrade head
```

Inside the container, the canonical module paths remain `python -m telegram_aggregator` for the service and `python -m telegram_aggregator.login` for login.

## Codex Role Wrapper

Use `bin/codex-role` to launch Codex with a repository role from `docs/roles`.

```bash
bin/codex-role tech-lead
bin/codex-role engineer fix parser bug
bin/codex-role product-owner refine backlog -- --model gpt-5.4
```

The wrapper always runs Codex with the repository root as `-C` and injects an initial prompt that points Codex to the selected role document.

Role-specific aliases are also available as thin wrappers around `bin/codex-role`.

```bash
bin/codex-tech-lead "plan refactor"
bin/codex-engineer fix parser bug -- --model gpt-5.4
bin/codex-product-owner refine backlog
```

For team-wide convenience, add the repository `bin/` directory to `PATH` in your shell setup.

```bash
export PATH="/path/to/Telegram-ggregator/bin:$PATH"
```
