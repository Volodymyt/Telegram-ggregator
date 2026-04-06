# M1 Intake To Candidate

Planning ID: 0024
Milestone: M1
Status: Draft
Last updated: 2026-04-06

## Goal

Deliver the first durable MVP slice from Telegram intake to candidate state without publication, while realigning the persistence contract to the locked M1 defaults before downstream aggregation and publish work begins.

## Scope

- Realign the storage contract from the current `message_records` and `event_records` shape to the locked `tg_message` and `event` model with independent status axes.
- Read new source messages from Telegram through the canonical runtime path, persist them once, and ignore duplicate deliveries safely on `(source_chat_id, source_message_id)`.
- Add the shared normalization and filter engine for include and exclude rules across message text and media captions.
- Extend the YAML runtime contract with one explicit stale-classification window so `outdated` handling is deterministic and operator-visible.
- Classify persisted intake rows as `outdated`, `filtered_out`, or `candidate`, and persist `event_type`, `event_signal`, `candidate_signature`, and the aggregation handoff state.
- Exclude event deduplication, `clear` lifecycle handling, publish jobs, publish recovery, and all target-channel publication behavior.

## Steps

1. Implement [M1 Intake state contract alignment](01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md) so M1 builds on the locked `tg_message` and `event` persistence contract instead of the older M0 placeholder schema.
2. Implement [M1 Source intake and message deduplication](02_0026_source_intake_and_message_deduplication/0026_source_intake_and_message_deduplication.md) to persist new Telegram source messages exactly once and enqueue only newly seen rows for processing.
3. Implement [M1 Normalization and filter engine](03_0027_normalization_and_filter_engine/0027_normalization_and_filter_engine.md) to preserve the documented matching semantics and to formalize the stale-classification runtime input.
4. Finish with [M1 Candidate classification pipeline](04_0028_candidate_classification_pipeline/0028_candidate_classification_pipeline.md) to move queued intake rows into durable `outdated`, `filtered_out`, or `candidate` state without starting event aggregation or publication.

## Risks

- The current M0 storage and repository artifacts still encode the older `message_records` and `event_records` contract, so M1 can inherit schema churn unless the realignment story lands first.
- `outdated` handling is required by the delivery plan but not yet represented in the YAML runtime contract, so leaving the stale rule implicit would push a product decision into implementation.
- The current runtime still has a thin queue-only bootstrap path, which can blur the boundary between reader, processing, and later aggregation concerns if M1 stories are allowed to overlap.
- Candidate metadata can drift between the filter engine and later aggregation work unless `event_type`, `event_signal`, and `candidate_signature` are persisted once and treated as the canonical handoff.

## Acceptance Criteria

- The M1 storage contract uses `tg_message` and `event` with independent `classification_status`, `aggregation_status`, and `publish_status` fields on `tg_message`.
- New source messages are read from Telegram, persisted once, normalized, and marked as `outdated`, `filtered_out`, or `candidate`.
- Source-message deduplication works on `(source_chat_id, source_message_id)`.
- Filter behavior covers `any` and `all` modes.
- Filter behavior covers `case_insensitive` and normalization toggles from the YAML contract.
- Messages already stale before classification are marked `outdated` without filter or candidate processing.
- Candidate classification persists `event_type`, `event_signal`, and `candidate_signature`.
- Queue-driven intake and processing operate end-to-end without publication.

## Links

- Parent plan: [MVP Delivery Plan](../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../project/architecture-spec.md)
- Depends on epic: [M0 Foundations Ready](../01_0001_foundations_ready/0001_foundations_ready.md)
- Story: [M1 Intake state contract alignment](01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
- Story: [M1 Source intake and message deduplication](02_0026_source_intake_and_message_deduplication/0026_source_intake_and_message_deduplication.md)
- Story: [M1 Normalization and filter engine](03_0027_normalization_and_filter_engine/0027_normalization_and_filter_engine.md)
- Story: [M1 Candidate classification pipeline](04_0028_candidate_classification_pipeline/0028_candidate_classification_pipeline.md)
