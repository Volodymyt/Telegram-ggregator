# M0 Bootstrap, observability, and test harness: runtime lifecycle and queue boundaries

Planning ID: 0020
Status: Ready
Last updated: 2026-03-15

## Goal

Define the canonical runtime lifecycle in `bootstrap/` so later workers, health hooks, and runtime integrations plug into one startup, queue, and shutdown contract.

## Scope

- Define the bootstrap-owned runtime context for settings, shared queue instances, registered runtime components, and startup state.
- Establish the canonical startup order after configuration and storage readiness are already available from earlier M0 stories.
- Create the processing, candidate, and publish queue boundaries without attaching concrete business workers.
- Define graceful shutdown sequencing and ownership for registered runtime components.
- Exclude Telethon client implementation details, health endpoint payload design, and bootstrap test fixtures.

## Steps

1. Define the `bootstrap/` modules or types that own runtime context, component registration, and queue lifecycle.
2. Create the in-process queue boundaries required by the architecture spec without embedding intake, processing, aggregation, or publish logic.
3. Implement the canonical startup orchestration that consumes validated settings and storage readiness before runtime components register.
4. Implement graceful shutdown sequencing so registered runtime components stop cleanly and predictably.

## Risks

- The runtime context can become a catch-all container if ownership of queues, component registration, and lifecycle state is not explicit.
- Queue creation can accidentally lock in later business assumptions if the boundaries are not kept generic at M0.

## Acceptance Criteria

- One canonical bootstrap entrypoint owns runtime context creation, queue creation, and worker-registration boundaries.
- The startup order is explicit enough that later stories can attach concrete runtime components without changing lifecycle ownership.
- Graceful shutdown ordering is defined clearly enough for later runtime components to stop cleanly without redefining the bootstrap contract.
- No concrete intake, processing, candidate-aggregation, or publish worker behavior is implemented in this task.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Bootstrap, observability, and test harness](../0019_bootstrap_observability_test_harness.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on story: [M0 Config and login contract](../../02_0007_config_login_contract/0007_config_login_contract.md)
- Depends on story: [M0 Storage contract and readiness](../../04_0015_storage_contract_readiness/0015_storage_contract_readiness.md)
