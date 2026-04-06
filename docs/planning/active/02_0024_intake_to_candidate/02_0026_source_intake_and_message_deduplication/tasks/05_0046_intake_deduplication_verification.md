# M1 Source intake and message deduplication: intake deduplication verification

Planning ID: 0046
Status: Draft
Last updated: 2026-04-06

## Goal

Protect the source-intake deduplication contract with focused verification so duplicate Telegram deliveries cannot silently create duplicate rows or duplicate downstream work.

## Scope

- Add focused verification for intake mapping from Telethon events into the canonical persisted shape.
- Verify that `raw_text` stores message text for plain messages and caption text for media-backed messages.
- Verify insert-once idempotency on `(source_chat_id, source_message_id)`.
- Verify that only first-seen rows are enqueued and duplicate deliveries remain a no-op after dedup confirmation.
- Exclude filter evaluation, stale classification, candidate processing, event deduplication, and publication behavior.

## Steps

1. Add tests that cover intake mapping into the canonical persisted fields, including the `raw_text` text-versus-caption rule.
2. Add tests that prove source-message persistence is idempotent on `(source_chat_id, source_message_id)`.
3. Add tests that prove only newly created rows are enqueued for downstream processing.
4. Add tests that prove duplicate deliveries become a durable no-op without re-enqueueing work.

## Risks

- Without focused verification, duplicate deliveries can regress into double inserts or double queue handoff without immediate visibility.
- If mapping coverage omits caption-backed messages, later processing can inherit the wrong `raw_text` contract.
- Mixing downstream filter or candidate checks into this task would blur ownership and duplicate later M1 coverage.

## Acceptance Criteria

- Automated tests cover intake mapping for plain-text and media-caption Telegram messages.
- Automated tests prove insert-once idempotency on `(source_chat_id, source_message_id)`.
- Automated tests prove only first-seen rows are enqueued.
- Automated tests prove duplicate deliveries do not re-enqueue work.
- The verification scope stays limited to source intake and deduplication behavior.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Source intake and message deduplication](../0026_source_intake_and_message_deduplication.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [02_0034_intake_mapping_and_raw_text_surface.md](02_0034_intake_mapping_and_raw_text_surface.md)
- Depends on task: [03_0035_insert_once_source_persistence.md](03_0035_insert_once_source_persistence.md)
- Depends on task: [04_0036_queue_enqueue_and_duplicate_delivery_handling.md](04_0036_queue_enqueue_and_duplicate_delivery_handling.md)
