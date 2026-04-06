# M1 Candidate classification pipeline: fresh-row normalization and filter classification

Planning ID: 0043
Status: Draft
Last updated: 2026-04-06

## Goal

Compute processing-owned `normalized_text` for fresh intake rows and apply the filter engine so M1 can persist `filtered_out` or `candidate` outcomes deterministically.

## Scope

- Compute and persist processing-owned `normalized_text` for fresh rows.
- Apply the documented filter engine after the stale check has passed.
- Persist `classification_status='filtered_out'` or `classification_status='candidate'` for fresh rows.
- Exclude worker wiring, stale handling, candidate metadata and aggregation handoff, event creation or deduplication, and publication.

## Steps

1. Normalize the persisted intake text surface for fresh rows using the shared processing-owned normalization helpers.
2. Run the filter engine on the normalized input after stale handling has already completed.
3. Persist the fresh-row classification result as either `filtered_out` or `candidate`.

## Risks

- If normalization is not shared with the documented filter engine, matching semantics can drift between stories.
- Writing normalized text before the stale check would waste work and blur the classification order.
- Combining aggregation handoff into this task would make the classification boundary harder to verify.

## Acceptance Criteria

- Fresh rows persist processing-owned `normalized_text` before filter classification.
- Filter evaluation runs only after stale handling.
- Fresh rows become either `filtered_out` or `candidate`.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Candidate classification pipeline](../0028_candidate_classification_pipeline.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [02_0042_stale_message_short_circuit.md](02_0042_stale_message_short_circuit.md)
- Depends on story: [M1 Normalization and filter engine](../../03_0027_normalization_and_filter_engine/0027_normalization_and_filter_engine.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
