# M1 Source intake and message deduplication: queue enqueue and duplicate delivery handling

Planning ID: 0036
Status: Draft
Last updated: 2026-04-06

## Goal

Enqueue only newly created source-message rows for downstream processing and keep duplicate deliveries as a no-op after the durable insert decision is known.

## Scope

- Enqueue only first-seen `tg_message` rows into the processing queue.
- Treat duplicate source-message deliveries as a safe no-op after dedup confirmation.
- Keep the enqueue decision tied to the durable insert result.
- Exclude reader subscription, intake mapping, filter evaluation, candidate classification, event deduplication, and publication.

## Steps

1. Use the durable insert result to decide whether the new intake row enters the processing queue.
2. Enqueue only rows created by a first-seen source-message insert.
3. Make duplicate deliveries observable as a deduplication success without re-enqueueing work.

## Risks

- If queueing is decoupled from the insert result, duplicate deliveries can create double processing.
- Queue logic that grows beyond handoff semantics would blur the boundary with later processing stories.

## Acceptance Criteria

- Only newly created `tg_message` rows are enqueued for processing.
- Duplicate deliveries do not re-enqueue work.
- The queue handoff remains a thin boundary and does not absorb later filter or candidate logic.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Source intake and message deduplication](../0026_source_intake_and_message_deduplication.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [03_0035_insert_once_source_persistence.md](03_0035_insert_once_source_persistence.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
