# M0 Bootstrap, observability, and test harness: observability and health surface

Planning ID: 0022
Status: Done
Last updated: 2026-05-02

## Goal

Establish the default runtime observability surface so operators can see high-level bootstrap readiness without duplicating lower-level storage or Telegram checks.

## Scope

- Define structured JSON logging as the default output contract for canonical bootstrap entrypoints.
- Aggregate high-level readiness from storage readiness, Telegram client bootstrap readiness, and worker liveness.
- Expose a lightweight HTTP health endpoint or equivalent container health surface for the canonical runtime.
- Keep the health surface high-level and avoid deep diagnostics, metrics backends, or feature-level event logging.
- Exclude storage-specific health checks already owned by storage readiness work.

## Steps

1. Define the default structured logging contract for canonical bootstrap startup, steady-state lifecycle, and shutdown events.
2. Model the readiness aggregation contract from storage readiness, Telegram client bootstrap readiness, and worker lifecycle state.
3. Implement a lightweight health endpoint or equivalent container health surface that reports those readiness states at a high level.
4. Document the boundary between this high-level health surface and deeper diagnostics reserved for later milestones.

## Risks

- Health reporting can give false confidence if it duplicates lower-level checks poorly or blurs readiness with deeper operational diagnostics.
- Logging can become inconsistent quickly if the default JSON contract is not defined before later runtime stories begin emitting events.

## Acceptance Criteria

- Structured JSON logs are the default runtime output for canonical bootstrap entrypoints.
- The health surface reports Telegram client bootstrap readiness, Postgres readiness, and worker liveness at a high level.
- The observability layer reuses the storage readiness hook and Telegram bootstrap readiness signal instead of reimplementing those checks.
- This task does not introduce deep diagnostics, metrics infrastructure, or feature-specific observability contracts.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Bootstrap, observability, and test harness](../0019_bootstrap_observability_test_harness.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0020_runtime_lifecycle_queue_boundaries.md](01_0020_runtime_lifecycle_queue_boundaries.md)
- Depends on task: [02_0021_telegram_client_bootstrap.md](02_0021_telegram_client_bootstrap.md)
- Depends on task: [02_0017_startup_readiness_hooks.md](../../04_0015_storage_contract_readiness/tasks/02_0017_startup_readiness_hooks.md)
