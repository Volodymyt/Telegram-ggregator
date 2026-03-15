# M0 Storage contract and readiness: startup readiness and migration hooks

Planning ID: 0017
Status: Ready
Last updated: 2026-03-15

## Goal

Expose one storage initialization path that proves Postgres reachability and migration health before runtime workers begin.

## Scope

- Implement storage initialization that opens the async engine, probes database connectivity, and executes or validates migrations at startup.
- Distinguish operator-facing failures for database reachability versus migration execution.
- Export a narrow readiness contract that the bootstrap and health layers can consume.
- Exclude general worker lifecycle management and health endpoint implementation, which belong to the bootstrap story.

## Steps

1. Implement the async engine initialization path for canonical storage readiness.
2. Add a connectivity probe that fails fast when Postgres is unreachable.
3. Add migration execution or validation to the same startup path.
4. Expose storage readiness results and distinct failure types for consumption by the bootstrap and health layers.

## Risks

- Startup becomes brittle if connectivity and migration failures are surfaced through the same opaque error path.
- Temporary bootstrap logic here would later conflict with the canonical runtime bootstrap story.

## Acceptance Criteria

- One storage startup hook verifies both database connectivity and schema readiness.
- Connectivity failures and migration failures are surfaced as distinct operator-facing errors.
- The readiness contract is narrow enough for reuse by bootstrap and health without duplicating storage checks.
- The task does not reimplement broader runtime lifecycle concerns outside storage readiness.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Storage contract and readiness](../0015_storage_contract_readiness.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0013_storage_surface_alembic.md](../../03_0012_storage_foundation/tasks/01_0013_storage_surface_alembic.md)
- Depends on task: [02_0014_schema_baseline.md](../../03_0012_storage_foundation/tasks/02_0014_schema_baseline.md)
