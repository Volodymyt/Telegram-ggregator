# M0 Storage bootstrap: startup readiness and migration hooks

Status: Ready
Owner: TBD
Last updated: 2026-03-14

## Goal

Expose one storage initialization path that proves Postgres reachability and migration health before runtime workers begin.

## Scope

- Implement storage initialization that opens the async engine, probes database connectivity, and executes or validates migrations at startup.
- Distinguish operator-facing failures for database reachability versus migration execution.
- Export a narrow readiness contract that the bootstrap and health layers can consume.
- Exclude general worker lifecycle management and health endpoint implementation, which belong to the bootstrap story.

## Dependencies

- [2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md](2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md)
- [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)

## Steps

1. Implement the async engine initialization path for storage bootstrap.
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

- Parent epic: [2026-03-14-epic-m0-foundations-ready.md](2026-03-14-epic-m0-foundations-ready.md)
- Parent story: [2026-03-14-story-m0-storage-bootstrap.md](2026-03-14-story-m0-storage-bootstrap.md)
- Depends on task: [2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md](2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md)
- Depends on task: [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)
- Parent plan: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [../../project/architecture-spec.md](../../project/architecture-spec.md)
