# M0 Foundations Ready

Planning ID: 0001
Milestone: M0
Status: Active
Last updated: 2026-03-15

## Goal

Establish the executable MVP baseline so later slices can add intake, aggregation, and publication behavior without reopening runtime, storage, or operator-contract decisions.

## Scope

- Replace the legacy execution path with the canonical package root under `src/telegram_aggregator/`.
- Align local and Docker runtime startup on one entrypoint contract.
- Lock the env and YAML configuration contract, including both supported login paths.
- Establish the storage package surface, migration mechanism, and the initial durable schema baseline before runtime wiring depends on them.
- Add the minimum storage repository boundary, startup readiness hooks, storage verification, runtime bootstrap ordering, worker lifecycle management, structured logging, lightweight health reporting, and test scaffolding.
- Exclude Telegram intake, filter evaluation, candidate aggregation, and publication logic beyond the interfaces needed to bootstrap the service.

## Steps

1. Establish the canonical package and runtime contract so every later story builds on the same import and startup path.
2. Define and validate the env and YAML contract, including `LOGIN=1` compatibility and the primary `python -m telegram_aggregator.login` flow.
3. Lock the canonical storage package surface, Alembic integration, and the initial durable schema baseline.
4. Add the minimum storage repository boundary, startup readiness hook, and storage verification so runtime bootstrap can consume one stable storage contract.
5. Add bootstrap ordering, Telegram client bootstrap readiness, lifecycle management, health visibility, structured logs, and test scaffolding to make later slices executable and verifiable.

## Risks

- The legacy `src/Telegram-aggregator/` path may still be referenced by runtime or container assets and must stop being the execution contract.
- Config validation can drift from the documented contract if env parsing, YAML parsing, and login handling are implemented independently.
- Storage foundation work can still leak downstream churn if schema and migration decisions are mixed with repository and runtime readiness decisions in the same delivery slice.
- Health and test scaffolding can become shallow if they do not expose Telegram client bootstrap readiness, Postgres readiness, and worker liveness clearly enough for operators.

## Acceptance Criteria

- The repository boots through the canonical package under `src/telegram_aggregator/`, and no supported local or Docker startup path still uses `src/Telegram-aggregator/` as the runtime contract.
- Docker and local runtime use the same service entrypoint contract and the same startup expectations.
- The dependency baseline is explicit and reproducible for runtime, migrations, configuration loading, observability, and tests.
- The service starts and stops cleanly through the canonical bootstrap path without placeholder runtime loops.
- Config validation fails fast on invalid env or YAML input before the service enters steady-state startup.
- Config validation covers source and target identifier formats, queue sizes, `LOG_LEVEL`, `DRY_RUN`, normalization toggles, filter mode semantics including the documented `all`-mode consistency rule, and both supported login modes.
- Both supported login entry paths are executable and aligned on one session-bootstrap contract: normal startup works with an existing session file, and both `LOGIN=1` and `python -m telegram_aggregator.login` create or validate the configured session path with distinct operator-facing errors on failure.
- PostgreSQL connectivity, migration execution, and one initial durable schema baseline are wired through one canonical storage path before runtime bootstrap depends on them.
- The storage layer exposes the minimum repository boundary and one reusable readiness hook needed for later reader, processing, aggregation, publish, and bootstrap work without reopening the storage contract.
- Queue creation, worker-registration boundaries, and bootstrap ordering are explicit enough for later stories to attach concrete workers without changing the M0 runtime structure.
- Structured JSON logs are the default runtime output format.
- A lightweight health endpoint or equivalent container health surface exposes readiness at a high level for Telegram client bootstrap, Postgres, and worker liveness.
- Automated tests run against the canonical package layout and cover bootstrap-oriented behavior, config validation, login/session handling, and storage foundation plus storage readiness expectations.

## Links

- Parent plan: [MVP Delivery Plan](../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../project/architecture-spec.md)
- Story: [M0 Runtime and package contract](01_0002_runtime_package_contract/0002_runtime_package_contract.md)
- Story: [M0 Config and login contract](02_0007_config_login_contract/0007_config_login_contract.md)
- Story: [M0 Storage foundation](03_0012_storage_foundation/0012_storage_foundation.md)
- Story: [M0 Storage contract and readiness](04_0015_storage_contract_readiness/0015_storage_contract_readiness.md)
- Story: [M0 Bootstrap, observability, and test harness](05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md)
