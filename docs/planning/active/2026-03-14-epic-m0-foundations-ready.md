# M0 Foundations Ready

Status: Active
Owner: Tech Lead
Last updated: 2026-03-14

## Goal

Establish the executable MVP baseline so later slices can add intake, aggregation, and publication behavior without reopening runtime, storage, or operator-contract decisions.

## Scope

- Replace the legacy execution path with the canonical package root under `src/telegram_aggregator/`.
- Align local and Docker runtime startup on one entrypoint contract.
- Lock the env and YAML configuration contract, including both supported login paths.
- Wire PostgreSQL connectivity, migration execution, and the initial durable schema baseline.
- Add runtime bootstrap, worker lifecycle management, structured logging, lightweight health reporting, and test scaffolding.
- Exclude Telegram intake, filter evaluation, candidate aggregation, and publication logic beyond the interfaces needed to bootstrap the service.

## Current State

- `Dockerfile` still starts `python -m Telegram-aggregator`.
- `requirements.txt` is still a placeholder.
- `src/telegram_aggregator/` does not yet contain the target runtime modules.
- The repository still needs a canonical bootstrap path, config layer, storage layer, observability baseline, and test harness.

## Story Map

1. [M0 Runtime and package contract](2026-03-14-story-m0-runtime-package-contract.md)
2. [M0 Config and login contract](2026-03-14-story-m0-config-login-contract.md)
3. [M0 Storage bootstrap](2026-03-14-story-m0-storage-bootstrap.md)
4. [M0 Bootstrap, observability, and test harness](2026-03-14-story-m0-bootstrap-observability-test-harness.md)

## Steps

1. Establish the canonical package and runtime contract so every later story builds on the same import and startup path.
2. Define and validate the env and YAML contract, including `LOGIN=1` compatibility and the primary `python -m telegram_aggregator.login` flow.
3. Wire PostgreSQL and Alembic into bootstrap with a minimal but durable schema baseline.
4. Add lifecycle management, health visibility, structured logs, and test scaffolding to make later slices executable and verifiable.

## Risks

- The legacy `src/Telegram-aggregator/` path may still be referenced by runtime or container assets and must stop being the execution contract.
- Config validation can drift from the documented contract if env parsing, YAML parsing, and login handling are implemented independently.
- Storage bootstrap can make startup brittle if connectivity failures and migration failures do not fail fast with distinct operator-facing errors.
- Health and test scaffolding can become shallow if they do not expose Telegram readiness, Postgres readiness, and worker liveness clearly enough for operators.

## Acceptance Criteria

- The repository boots through the canonical package.
- Docker and local runtime point to the same entrypoint contract.
- Dependencies, migrations, config loading, login entrypoint, logging, and health baseline are in place.
- Tests can run against the new project structure.
- The service starts and stops cleanly without placeholder code.
- Config validation fails fast on invalid env or YAML input.
- Config validation covers source and target identifier formats, queue sizes, `LOG_LEVEL`, `DRY_RUN`, normalization toggles, and login modes.
- Postgres connectivity and migration execution are wired.
- The login command creates or validates a session file path.

## Links

- Parent plan: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Requirements: [../../project/requirements.md](../../project/requirements.md)
- Architecture spec: [../../project/architecture-spec.md](../../project/architecture-spec.md)
