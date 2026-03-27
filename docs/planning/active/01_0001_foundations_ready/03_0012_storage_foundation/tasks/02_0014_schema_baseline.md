# M0 Storage foundation: schema baseline for message and event records

Planning ID: 0014
Status: Done
Last updated: 2026-03-27

## Goal

Freeze the MVP durable-state contract for `message_records` and `event_records` so later milestones extend the schema instead of reopening foundational persistence design.

## Scope

- Define SQLAlchemy Core metadata for `message_records` and `event_records`.
- Encode the locked MVP message statuses, event states, publish statuses, foreign-key relation, timestamp fields, and nullability rules.
- Add the first Alembic revision that creates both tables together with required constraints and indexes.
- Exclude repository APIs, startup readiness checks, and business-state transitions beyond the baseline contract.

## Steps

1. Define SQLAlchemy Core table metadata for `message_records` and `event_records` in the canonical storage package.
2. Encode the unique constraint on `(source_chat_id, source_message_id)` and the baseline lookup indexes from the architecture spec.
3. Create the initial Alembic revision for the baseline schema.
4. Verify that the revision produces the same storage contract documented by the delivery plan and architecture spec.

## Risks

- Missing state fields now would force later milestones to rewrite the baseline instead of extending it.
- Introducing extra tables or ORM models would violate the locked MVP storage defaults.

## Acceptance Criteria

- The canonical metadata defines `message_records` and `event_records` with the locked MVP fields and relations.
- The initial Alembic revision creates both tables, the unique constraint on `(source_chat_id, source_message_id)`, and the required lookup indexes.
- The baseline schema uses SQLAlchemy Core only and does not introduce ORM models or non-MVP tables.
- A clean database can be migrated to the baseline schema without manual edits.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Storage foundation](../0012_storage_foundation.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0013_storage_surface_alembic.md](01_0013_storage_surface_alembic.md)
