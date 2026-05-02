# M0 Bootstrap, observability, and test harness

Planning ID: 0019
Status: Done
Last updated: 2026-05-02

## Goal

Make the canonical package bootable, observable, and testable so later slices can add runtime behavior without inventing lifecycle, Telegram bootstrap, or verification scaffolding midstream.

## Scope

- Define the service bootstrap sequence and graceful shutdown behavior for the canonical package.
- Add the minimum Telegram client bootstrap and session-readiness integration needed for normal startup and operator-visible health.
- Create the queue and worker-registration boundaries that later stories will fill with concrete intake, processing, aggregation, and publish behavior.
- Establish structured JSON logging as the runtime default.
- Add a lightweight HTTP health endpoint with readiness semantics for Telegram client bootstrap, Postgres, and worker liveness at a high level.
- Establish the bootstrap-oriented test harness for the canonical package layout without redefining storage-specific verification owned by earlier stories.
- Non-goals: implement Telegram intake logic, business worker behavior, full integration suites, or capacity and latency verification.

## Steps

1. Implement [M0 Bootstrap, observability, and test harness: runtime lifecycle and queue boundaries](tasks/01_0020_runtime_lifecycle_queue_boundaries.md) to define the canonical startup order, queue ownership, worker registration boundary, and graceful shutdown contract in `bootstrap/`.
2. Continue with [M0 Bootstrap, observability, and test harness: Telegram client bootstrap and session readiness](tasks/02_0021_telegram_client_bootstrap.md) to integrate the minimum Telethon startup and shutdown path into the canonical runtime lifecycle without adding reader behavior.
3. Implement [M0 Bootstrap, observability, and test harness: observability and health surface](tasks/03_0022_observability_health_surface.md) to make structured JSON logging and high-level readiness visible on top of the shared bootstrap and storage contracts.
4. Finish with [M0 Bootstrap, observability, and test harness: bootstrap verification harness](tasks/04_0023_bootstrap_verification_harness.md) to protect startup, shutdown, and health behavior without duplicating storage-specific verification.

## Risks

- Bootstrap ordering can become unstable if readiness checks and worker registration are interleaved without a clear lifecycle contract.
- Health reporting can give false confidence if it does not distinguish configuration success from Telegram client bootstrap readiness, database readiness, and worker liveness.
- Logging can become inconsistent if structured output is not defined before later stories start emitting runtime events.
- Test scaffolding can duplicate earlier storage coverage unless this story stays anchored on bootstrap entrypoints, health, and lifecycle concerns.

## Acceptance Criteria

- The service starts and stops cleanly through the canonical package bootstrap path.
- Normal startup integrates the canonical session/login contract with a minimal Telegram client bootstrap path that later runtime stories can extend without changing M0 startup structure.
- Queue creation and worker-registration boundaries are explicit enough for later stories to attach concrete workers without changing bootstrap structure.
- Structured JSON logs are the default runtime output format.
- A lightweight health endpoint exposes readiness for Telegram client bootstrap, Postgres, and worker liveness at a high level.
- Automated tests can run against the canonical package layout and cover bootstrap-oriented behavior without reowning storage-specific acceptance already covered earlier in M0.

## Links

- Parent epic: [M0 Foundations Ready](../0001_foundations_ready.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
- Depends on story: [M0 Config and login contract](../02_0007_config_login_contract/0007_config_login_contract.md)
- Depends on story: [M0 Storage contract and readiness](../04_0015_storage_contract_readiness/0015_storage_contract_readiness.md)
- Sequencing constraint: [M0 Bootstrap, observability, and test harness: observability and health surface](tasks/03_0022_observability_health_surface.md) starts only after [M0 Bootstrap, observability, and test harness: runtime lifecycle and queue boundaries](tasks/01_0020_runtime_lifecycle_queue_boundaries.md), [M0 Bootstrap, observability, and test harness: Telegram client bootstrap and session readiness](tasks/02_0021_telegram_client_bootstrap.md), and the storage readiness hook from [M0 Storage contract and readiness: startup readiness and migration hooks](../04_0015_storage_contract_readiness/tasks/02_0017_startup_readiness_hooks.md) are stable.
- Sequencing constraint: [M0 Bootstrap, observability, and test harness: bootstrap verification harness](tasks/04_0023_bootstrap_verification_harness.md) starts only after tasks `01` through `03` are stable and must reuse storage-specific verification owned by [M0 Storage contract and readiness: verification coverage](../04_0015_storage_contract_readiness/tasks/03_0018_verification_coverage.md) instead of duplicating it.
