# M0 Storage bootstrap

Status: Draft
Owner: Tech Lead
Last updated: 2026-03-14

## Goal

Establish PostgreSQL as the executable durable-state baseline so later slices can persist messages and events without revisiting the storage stack or migration contract.

## Scope

- Use PostgreSQL as the canonical durable store for the MVP.
- Use SQLAlchemy 2.x async engine and SQLAlchemy Core rather than ORM models.
- Set up Alembic as the schema migration mechanism for the service.
- Define the initial schema baseline centered on `message_records` and `event_records`, with fields and relations needed by later milestones.
- Wire startup-time database connectivity checks and migration execution into the bootstrap path.
- Define the repository-layer boundary expected by later reader, processing, aggregation, and publish stories.
- Non-goals: implement full business-state transitions, recovery loops, or feature-level repositories beyond the bootstrap contract.

## Steps

1. Establish the canonical storage stack with PostgreSQL, SQLAlchemy async Core, and Alembic.
2. Create the initial migration baseline for `message_records` and `event_records` using the internal contracts already locked by the delivery plan.
3. Wire database connectivity and migration execution into startup so storage readiness is known before runtime workers begin.
4. Define the repository boundary around message and event persistence so later stories can add behavior without changing the storage contract.

## Task Breakdown

1. [M0 Storage bootstrap: storage surface and Alembic scaffold](tasks/01_storage_surface_alembic.md)
   Lock the canonical storage package surface and Alembic scaffold on top of the already fixed runtime and config contracts.
2. [M0 Storage bootstrap: schema baseline for message and event records](tasks/02_schema_baseline.md)
   Define the baseline SQLAlchemy Core schema and the first Alembic revision for `message_records` and `event_records`.
3. [M0 Storage bootstrap: repository boundary and persistence primitives](tasks/03_repository_boundary.md)
   Establish the minimum stable repository contract for message and event persistence on the baseline schema.
4. [M0 Storage bootstrap: startup readiness and migration hooks](tasks/04_startup_readiness_hooks.md)
   Add one storage initialization path that proves database reachability and migration health before workers start.
5. [M0 Storage bootstrap: verification coverage](tasks/05_verification_coverage.md)
   Protect the storage bootstrap contract with automated coverage for migrations, readiness, and baseline persistence primitives.

## Execution Sequence

1. Start with [01_storage_surface_alembic.md](tasks/01_storage_surface_alembic.md), because every other storage task depends on the canonical package surface and Alembic scaffold.
2. Continue with [02_schema_baseline.md](tasks/02_schema_baseline.md), because the schema and first revision are the durable contract for all later storage work.
3. Then implement [03_repository_boundary.md](tasks/03_repository_boundary.md), because repository primitives must target the real baseline tables and constraints.
4. After that implement [04_startup_readiness_hooks.md](tasks/04_startup_readiness_hooks.md), because startup wiring must consume the same engine and migration contract rather than temporary bootstrap code.
5. Finish with [05_verification_coverage.md](tasks/05_verification_coverage.md), after the schema, repository, and readiness contracts are stable enough to verify together.

## Sequencing Notes

- Do not start this story before the runtime package and config/login stories have locked the canonical package path and database settings contract.
- The repository-boundary task and the startup-readiness task may overlap only after the schema-baseline task is stable, but both must consume the same engine, metadata, and migration contract created by the first two tasks.
- The bootstrap and observability story should consume the storage readiness hook produced here rather than reimplementing database checks.

## Risks

- Introducing ORM models would create an unnecessary abstraction mismatch against the locked architecture choice of SQLAlchemy Core.
- A schema baseline that omits key state fields can force later milestones to reopen persistence contracts instead of extending them.
- Startup can become brittle if connectivity checks and migration execution do not distinguish transient database reachability from migration errors.
- Repository boundaries can become too broad if bootstrap tries to encode later business logic instead of establishing only the storage contract.

## Acceptance Criteria

- PostgreSQL is the only supported canonical durable store for the MVP bootstrap path.
- The storage layer uses SQLAlchemy async Core and does not depend on ORM models.
- Alembic is wired and can execute the initial schema baseline for `message_records` and `event_records`.
- Startup checks database connectivity and fails clearly when connectivity or migration execution is not healthy.
- A repository boundary exists for message and event persistence that later stories can build on without redesigning the storage layer.

## Links

- Parent epic: [M0 Foundations Ready](../epic.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
