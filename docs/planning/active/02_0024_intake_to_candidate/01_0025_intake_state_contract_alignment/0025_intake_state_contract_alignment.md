# M1 Intake state contract alignment

Planning ID: 0025
Status: Draft
Last updated: 2026-04-06

## Goal

Realign the canonical persistence contract to the locked `tg_message` and `event` model before M1 intake, filtering, and classification behavior is added on top of storage.

## Scope

- Replace the current `message_records` and `event_records` schema contract with the locked `tg_message` and `event` tables.
- Split `tg_message` progress into `classification_status`, `aggregation_status`, and `publish_status` instead of one overloaded message status field.
- Rename the message-to-event relation surface from legacy `event_record_id` to canonical `event_id`, including the FK constraint and related metadata names.
- Preserve idempotent source-message persistence on `(source_chat_id, source_message_id)` and keep explicit transaction boundaries in the storage facade.
- Update repository primitives, storage metadata, migrations, readiness checks, and storage tests to the new canonical naming and state model.
- Exclude Telegram reader behavior, filter evaluation, candidate claiming, event deduplication, and publication logic.

## Steps

1. Define the canonical `tg_message` and `event` schema metadata with the locked M1 fields, nullability, constraints, indexes, and the renamed `event_id` relation surface.
2. Update the storage facade and repository boundary so later M1 stories can create, fetch, and update rows against the new split-status contract without exposing legacy `event_record_id` names.
3. Adjust migration and readiness coverage so the database contract stays queryable and verifiable after the table rename, relation rename, and status-model change.
4. Refresh storage-focused tests and planning references that still assume `message_records`, `event_records`, or the old single-status/`event_record_id` contract.

## Risks

- Schema realignment here can create avoidable churn if later M1 stories keep reaching back to rework names or status fields again.
- Carrying the old single-status model forward would force M2 and M3 to reopen storage decisions that are already locked by the delivery plan.
- Migration coverage can become shallow if it only renames tables without proving that the repository and readiness surfaces still match the canonical contract.

## Acceptance Criteria

- The canonical persistence model for active planning and implementation is `tg_message` and `event`, not `message_records` and `event_records`.
- `tg_message` exposes `classification_status`, `aggregation_status`, and `publish_status` with the locked status sets from the delivery plan.
- The canonical relation from `tg_message` to `event` is `event_id`, and migrations plus storage metadata no longer expose legacy FK, index, or constraint names tied to `event_record_id`.
- Idempotent source-message persistence remains defined on `(source_chat_id, source_message_id)`.
- The storage facade and repositories remain SQLAlchemy Core based and reusable by later reader, processing, aggregation, and publish stories without redesign.
- Migration and storage verification cover the realigned schema and repository contract.

## Links

- Parent epic: [M1 Intake To Candidate](../0024_intake_to_candidate.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
- Depends on epic: [M0 Foundations Ready](../../01_0001_foundations_ready/0001_foundations_ready.md)
- Depends on story: [M0 Storage foundation](../../01_0001_foundations_ready/03_0012_storage_foundation/0012_storage_foundation.md)
- Depends on story: [M0 Storage contract and readiness](../../01_0001_foundations_ready/04_0015_storage_contract_readiness/0015_storage_contract_readiness.md)
