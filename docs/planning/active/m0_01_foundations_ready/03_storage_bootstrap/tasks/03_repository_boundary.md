# M0 Storage bootstrap: repository boundary and persistence primitives

Status: Ready
Last updated: 2026-03-14

## Goal

Define the minimum stable persistence boundary that later reader, processing, aggregation, and publish stories can use without redesigning the storage layer.

## Scope

- Define the repository boundary for message and event persistence using SQLAlchemy Core only.
- Implement the minimum persistence primitives needed to create, fetch, and update `message_records` and `event_records`.
- Make idempotent source-message persistence and explicit transaction boundaries part of the storage contract.
- Exclude candidate claiming, event deduplication, publish recovery, and other later business workflows.

## Steps

1. Define the repository modules or interfaces for message and event persistence inside the canonical storage package.
2. Implement the minimum read/write primitives against the baseline schema without embedding future business decisions in the storage layer.
3. Make the source-message write path idempotent on `(source_chat_id, source_message_id)`.
4. Expose transaction boundaries that later stories can extend for candidate, event, and publish state changes.

## Risks

- Over-designing repositories now would leak later business logic into the storage layer.
- Under-specifying idempotency or transactions would force later milestones to reopen the storage contract.

## Acceptance Criteria

- The storage layer exposes a stable repository boundary for `message_records` and `event_records`.
- The first persistence primitives can create, fetch, and update baseline records against the canonical schema.
- Source-message persistence is explicitly idempotent on `(source_chat_id, source_message_id)`.
- The repository layer uses SQLAlchemy Core only and does not depend on ORM models.

## Links

- Parent epic: [M0 Foundations Ready](../../epic.md)
- Parent story: [M0 Storage bootstrap](../story.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [02_schema_baseline.md](02_schema_baseline.md)
