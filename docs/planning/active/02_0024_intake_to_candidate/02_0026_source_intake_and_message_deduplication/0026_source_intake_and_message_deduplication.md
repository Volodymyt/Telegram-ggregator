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

1. Implement [M1 Source intake and message deduplication: Telegram source subscription and adapter boundary](tasks/01_0033_telegram_source_subscription_and_adapter_boundary.md) to wire configured Telegram sources through the canonical runtime path without bypassing the existing Telethon adapter boundary.
2. Implement [M1 Source intake and message deduplication: intake mapping and raw text surface](tasks/02_0034_intake_mapping_and_raw_text_surface.md) to normalize Telethon events into the canonical persisted intake shape, including the `raw_text` convention for message text and media captions.
3. Implement [M1 Source intake and message deduplication: insert-once source persistence](tasks/03_0035_insert_once_source_persistence.md) to persist new `tg_message` rows with the initial M1 state contract and safe deduplication on `(source_chat_id, source_message_id)`.
4. Implement [M1 Source intake and message deduplication: queue enqueue and duplicate delivery handling](tasks/04_0036_queue_enqueue_and_duplicate_delivery_handling.md) to enqueue only first-seen rows and make duplicate deliveries a durable no-op beyond the insert result.
5. Finish with [M1 Source intake and message deduplication: intake deduplication verification](tasks/05_0046_intake_deduplication_verification.md) to protect intake mapping, insert-once persistence, and queue no-op duplicate handling with focused tests.

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
