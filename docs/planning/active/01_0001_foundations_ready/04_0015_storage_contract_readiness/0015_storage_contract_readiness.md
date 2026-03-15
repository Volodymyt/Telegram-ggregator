# M0 Storage contract and readiness

Planning ID: 0015
Status: Draft
Last updated: 2026-03-15

## Goal

Expose one stable storage contract for repositories, startup readiness, and storage verification so runtime bootstrap and later feature slices can build on durable persistence behavior without redesigning the storage layer.

## Scope

- Define the repository-layer boundary for message and event persistence on top of the canonical storage package and schema baseline.
- Implement the minimum persistence primitives needed by later reader, processing, aggregation, and publish stories.
- Add one storage readiness path that distinguishes database reachability from migration health.
- Protect the storage contract with focused automated verification for repositories, migrations, and readiness behavior.
- Non-goals: redefine schema baseline fields, rework the storage package surface, or absorb broader runtime lifecycle and health endpoint concerns.

## Steps

1. Implement [M0 Storage contract and readiness: repository boundary and persistence primitives](tasks/01_0016_repository_boundary.md) to establish the minimum stable repository contract on the baseline schema.
2. Implement [M0 Storage contract and readiness: startup readiness and migration hooks](tasks/02_0017_startup_readiness_hooks.md) to add one storage initialization path that proves database reachability and migration health before workers start.
3. Finish with [M0 Storage contract and readiness: verification coverage](tasks/03_0018_verification_coverage.md) to protect migrations, readiness, and baseline persistence primitives with automated coverage.

## Risks

- Repository boundaries can become too broad if this story starts encoding later business workflows instead of only the storage contract.
- Startup will remain brittle if readiness still surfaces connectivity and migration failures through the same opaque error path.
- Storage verification can overlap awkwardly with broader bootstrap tests unless this story stays focused on storage-specific acceptance signals.

## Acceptance Criteria

- A repository boundary exists for message and event persistence that later stories can build on without redesigning the storage layer.
- The first persistence primitives can create, fetch, and update baseline records, including idempotent source-message persistence on `(source_chat_id, source_message_id)`.
- One storage readiness hook verifies both database connectivity and schema readiness with distinct operator-facing failures.
- Automated verification covers the baseline migration path, storage readiness behavior, and the first repository primitives without expanding into non-storage workflows.

## Links

- Parent epic: [M0 Foundations Ready](../0001_foundations_ready.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
- Depends on story: [M0 Runtime and package contract](../01_0002_runtime_package_contract/0002_runtime_package_contract.md)
- Depends on story: [M0 Config and login contract](../02_0007_config_login_contract/0007_config_login_contract.md)
- Depends on story: [M0 Storage foundation](../03_0012_storage_foundation/0012_storage_foundation.md)
- Downstream reference: [M0 Bootstrap, observability, and test harness](../05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md) must consume the storage readiness hook from this story instead of reimplementing database checks.
