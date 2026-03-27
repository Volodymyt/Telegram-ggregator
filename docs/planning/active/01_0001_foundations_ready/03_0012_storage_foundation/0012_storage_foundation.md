# M0 Storage foundation

Planning ID: 0012
Status: Done
Last updated: 2026-03-27

## Goal

Establish the canonical storage package, migration mechanism, and durable schema baseline so later slices can add persistence behavior without reopening foundational storage decisions.

## Scope

- Use PostgreSQL as the canonical durable store for the MVP.
- Use SQLAlchemy 2.x async engine and SQLAlchemy Core rather than ORM models.
- Set up Alembic as the schema migration mechanism for the service.
- Define the initial schema baseline centered on `message_records` and `event_records`, with fields and relations needed by later milestones.
- Lock the canonical storage package surface that later repository and bootstrap work must reuse.
- Non-goals: implement repository primitives, startup readiness hooks, runtime lifecycle wiring, or feature-level storage behavior beyond the foundation contract.

## Steps

1. Implement [M0 Storage foundation: storage surface and Alembic scaffold](tasks/01_0013_storage_surface_alembic.md) to lock the canonical storage package surface and Alembic scaffold on top of the runtime and config contracts.
2. Continue with [M0 Storage foundation: schema baseline for message and event records](tasks/02_0014_schema_baseline.md) to define the baseline SQLAlchemy Core schema and the first Alembic revision for `message_records` and `event_records`.

## Risks

- Introducing ORM models would create an unnecessary abstraction mismatch against the locked architecture choice of SQLAlchemy Core.
- A schema baseline that omits key state fields can force later milestones to reopen persistence contracts instead of extending them.
- Ad hoc storage module boundaries here would force later repository and bootstrap stories to reshape the package contract instead of building on it.

## Acceptance Criteria

- PostgreSQL is the only supported canonical durable store for the MVP storage foundation.
- The storage layer uses SQLAlchemy async Core and does not depend on ORM models.
- Alembic is wired and can execute the initial schema baseline for `message_records` and `event_records`.
- The canonical storage package surface is stable enough that later repository and runtime stories can consume it without redefining the storage entrypoint.

## Links

- Parent epic: [M0 Foundations Ready](../0001_foundations_ready.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
- Depends on story: [M0 Runtime and package contract](../01_0002_runtime_package_contract/0002_runtime_package_contract.md)
- Depends on story: [M0 Config and login contract](../02_0007_config_login_contract/0007_config_login_contract.md)
- Downstream reference: [M0 Storage contract and readiness](../04_0015_storage_contract_readiness/0015_storage_contract_readiness.md) must reuse the same engine, metadata, and migration contract defined by this story.
