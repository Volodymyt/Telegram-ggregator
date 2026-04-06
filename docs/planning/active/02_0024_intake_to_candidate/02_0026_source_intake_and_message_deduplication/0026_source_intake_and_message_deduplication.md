# M1 Source intake and message deduplication

Planning ID: 0026
Status: Draft
Last updated: 2026-04-06

## Goal

Persist newly delivered Telegram source messages exactly once and enqueue only newly seen rows for processing, so M1 starts from one durable intake path rather than an in-memory placeholder queue.

## Scope

- Register the configured Telegram sources through the canonical runtime and reader boundary.
- Map incoming Telethon message events into one intake record shape that captures source identifiers, source metadata, the raw text surface stored in `raw_text` (message text or media caption), media presence, and receive time.
- Persist new source messages with the initial M1 state contract and ignore duplicate deliveries safely on `(source_chat_id, source_message_id)`.
- Enqueue only newly created `tg_message` rows into the processing queue.
- Exclude filter evaluation, stale classification, event-level deduplication, and any publish behavior.

## Steps

1. Define the reader-owned intake mapping from Telethon message events into the canonical persisted source-message fields, including the convention that `raw_text` stores either the message text or the media caption surface.
2. Wire configured source subscription into the runtime bootstrap without bypassing the existing Telethon adapter boundary.
3. Persist incoming messages through the realigned storage contract with initial `classification_status='pending'`, `aggregation_status='new'`, and `publish_status='new'`.
4. Enqueue only first-seen rows for downstream processing and make duplicate deliveries a no-op beyond safe dedup confirmation.

## Risks

- Mixing reader concerns with later processing logic would make it hard to reason about which component owns source deduplication versus candidate classification.
- Duplicate Telegram deliveries can still leak into downstream queues if the persistence and enqueue decision are not tied to the same durable insert-once result.
- Source metadata capture can drift from future attribution needs if M1 does not persist the minimal source title and source link surface now.

## Acceptance Criteria

- Telethon reads the configured sources through the canonical runtime path.
- New source messages are persisted once with the initial `tg_message` state contract.
- Duplicate source-message deliveries are ignored safely on `(source_chat_id, source_message_id)` and do not re-enqueue work.
- Persisted intake rows retain the message text surface in `raw_text`, using the caption when the Telegram message is media-backed, and keep the source metadata needed by later M2 publication work.
- The reader stays thin and does not absorb filter, aggregation, or publish decisions.

## Links

- Parent epic: [M1 Intake To Candidate](../0024_intake_to_candidate.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
- Depends on story: [M1 Intake state contract alignment](../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
- Depends on story: [M0 Bootstrap, observability, and test harness](../../01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md)
