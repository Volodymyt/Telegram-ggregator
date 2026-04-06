# M1 Intake state contract alignment: storage facade and repository boundary update

Planning ID: 0030
Status: Draft
Last updated: 2026-04-06

## Goal

Update the storage facade and repository boundary so later M1 stories can create, fetch, and update rows against the canonical split-status contract.

## Scope

- Update the repository modules or interfaces that expose message and event persistence.
- Keep the persistence layer SQLAlchemy Core based and reusable by later reader, processing, aggregation, and publish work.
- Preserve explicit transaction boundaries in the storage facade.
- Keep source-message persistence idempotent on `(source_chat_id, source_message_id)`.
- Exclude migration authoring, startup readiness checks, reader behavior, filter evaluation, and candidate processing.

## Steps

1. Update the repository APIs to accept and return the canonical `tg_message` and `event` shapes.
2. Remove legacy `event_record_id` naming from the storage facade and repository boundary.
3. Keep transaction handling explicit so later stories can compose multi-step persistence work safely.
4. Preserve idempotent source-message persistence on `(source_chat_id, source_message_id)` through the canonical write path.

## Risks

- If the repository boundary still exposes legacy names, later M1 stories will have to translate between two competing contracts.
- Hiding transaction scope inside helper methods would make later classification and aggregation work harder to reason about.
- Relaxing the idempotency contract here would allow duplicate intake rows to leak into later processing slices.

## Acceptance Criteria

- The storage facade exposes a stable repository boundary for `tg_message` and `event`.
- Repository primitives can create, fetch, and update rows against the canonical M1 contract.
- Source-message persistence is explicitly idempotent on `(source_chat_id, source_message_id)`.
- The persistence layer remains SQLAlchemy Core only and does not depend on ORM models.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Intake state contract alignment](../0025_intake_state_contract_alignment.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0029_canonical_schema_metadata_and_relation_surface.md](01_0029_canonical_schema_metadata_and_relation_surface.md)
- Depends on task: [01_0016_repository_boundary.md](../../../01_0001_foundations_ready/04_0015_storage_contract_readiness/tasks/01_0016_repository_boundary.md)
