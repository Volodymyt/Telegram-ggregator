# M1 Candidate classification pipeline: candidate metadata and aggregation handoff

Planning ID: 0044
Status: Draft
Last updated: 2026-04-06

## Goal

Persist the candidate-only match metadata and mark candidate rows for the durable M2 aggregation handoff without starting event or publish behavior.

## Scope

- Persist `event_type` and `event_signal` for candidate rows.
- Transition candidate rows to `aggregation_status='queued'` as the durable handoff into later M2 and M3 work.
- Keep candidate handoff separate from signature generation, event creation or deduplication, `clear` lifecycle handling, and publication.
- Exclude worker wiring, stale handling, and filter evaluation.

## Steps

1. Persist candidate match metadata for rows already classified as `candidate`.
2. Update the candidate handoff state to `aggregation_status='queued'`.
3. Stop at the handoff boundary without building `candidate_signature` or starting event logic.

## Risks

- If candidate metadata is not persisted here, later aggregation stories will have to infer classification state from a weaker handoff.
- Building event or publish behavior here would break the M1/M2 boundary.
- Letting aggregation handoff leak into classification logic would make the state transitions harder to reason about.

## Acceptance Criteria

- Candidate rows persist `event_type` and `event_signal`.
- Candidate rows transition to `aggregation_status='queued'`.
- No event creation, event deduplication, or publication behavior starts in this task.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Candidate classification pipeline](../0028_candidate_classification_pipeline.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [03_0043_fresh_row_normalization_and_filter_classification.md](03_0043_fresh_row_normalization_and_filter_classification.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
