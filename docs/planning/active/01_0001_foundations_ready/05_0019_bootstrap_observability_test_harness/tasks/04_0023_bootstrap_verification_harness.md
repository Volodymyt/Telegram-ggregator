# M0 Bootstrap, observability, and test harness: bootstrap verification harness

Planning ID: 0023
Status: Done
Last updated: 2026-05-02

## Goal

Protect the canonical bootstrap path with automated verification and minimal shared fixtures focused on startup, shutdown, readiness aggregation, and health behavior.

## Scope

- Add bootstrap-oriented fixtures, stubs, or helpers needed to test runtime lifecycle behavior in the canonical package layout.
- Verify startup success, startup failure propagation, graceful shutdown, and health responses.
- Verify bootstrap behavior on top of the shared storage readiness and Telegram bootstrap contracts without retesting storage internals.
- Exclude storage migration tests, repository tests, and end-to-end intake or publication flows.

## Steps

1. Add the minimum shared test helpers or fixtures needed to exercise canonical bootstrap entrypoints and registered runtime components.
2. Add tests for startup success and failure propagation across validated config, storage readiness, and Telegram bootstrap readiness dependencies.
3. Add tests for graceful shutdown and worker lifecycle boundaries.
4. Add health-surface tests that verify aggregated readiness behavior without duplicating earlier storage verification.

## Risks

- Test fixtures can become a second bootstrap implementation if they model runtime behavior too deeply instead of exercising the real bootstrap contract.
- This task can easily duplicate storage verification unless the test surface stays focused on lifecycle and readiness aggregation.

## Acceptance Criteria

- Automated tests cover canonical bootstrap startup, shutdown, and failure propagation behavior.
- Automated tests cover health responses produced from aggregated storage readiness, Telegram bootstrap readiness, and worker-liveness state.
- Shared fixtures stay limited to bootstrap-oriented behavior and do not reown storage-specific migration or repository verification.
- This task does not expand into end-to-end Telegram intake or publication testing.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Bootstrap, observability, and test harness](../0019_bootstrap_observability_test_harness.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0020_runtime_lifecycle_queue_boundaries.md](01_0020_runtime_lifecycle_queue_boundaries.md)
- Depends on task: [02_0021_telegram_client_bootstrap.md](02_0021_telegram_client_bootstrap.md)
- Depends on task: [03_0022_observability_health_surface.md](03_0022_observability_health_surface.md)
- Depends on task: [03_0018_verification_coverage.md](../../04_0015_storage_contract_readiness/tasks/03_0018_verification_coverage.md)
