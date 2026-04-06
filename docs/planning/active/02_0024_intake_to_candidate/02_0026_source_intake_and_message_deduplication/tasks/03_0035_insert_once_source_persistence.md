# M1 Source intake and message deduplication: insert-once source persistence

Planning ID: 0035
Status: Draft
Last updated: 2026-04-06

## Goal

Persist new source messages exactly once through the canonical storage contract so duplicate Telegram deliveries cannot create duplicate intake rows.

## Scope

- Persist newly seen source messages with the initial M1 state contract.
- Enforce idempotency on `(source_chat_id, source_message_id)`.
- Use the canonical `tg_message` storage contract realigned in story `0025`.
- Exclude queue enqueue behavior, reader subscription, filter evaluation, candidate classification, and publication.

## Steps

1. Persist new source messages through the canonical storage boundary with the initial `classification_status`, `aggregation_status`, and `publish_status` values.
2. Make the write path idempotent on `(source_chat_id, source_message_id)` so duplicate deliveries do not produce duplicate rows.
3. Keep the persistence path aligned with the locked `tg_message` contract from the storage realignment story.

## Risks

- If the insert-once decision is not tied to the durable write result, duplicate deliveries can still leak into downstream work.
- Reopening the status model here would duplicate the storage contract work already locked in `0025`.

## Acceptance Criteria

- New source messages are persisted once through the canonical storage contract.
- Duplicate deliveries on `(source_chat_id, source_message_id)` are handled safely and do not create duplicate intake rows.
- Initial M1 status values are applied on insert and remain consistent with the realigned storage contract.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Source intake and message deduplication](../0026_source_intake_and_message_deduplication.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [02_0034_intake_mapping_and_raw_text_surface.md](02_0034_intake_mapping_and_raw_text_surface.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
