# M1 Candidate classification pipeline: classification pipeline verification

Planning ID: 0045
Status: Draft
Last updated: 2026-04-06

## Goal

Protect queue recovery, stale handling, fresh classification, and aggregation handoff with focused verification so M1 classification stays aligned with the documented contract.

## Scope

- Add focused tests for startup recovery of persisted `pending` rows.
- Add tests for stale short-circuit behavior before filter evaluation.
- Add tests for fresh-row normalization, filter classification, and candidate handoff state transitions.
- Keep the test surface limited to the classification pipeline.
- Exclude candidate signature generation, event creation or deduplication, `clear` lifecycle handling, publish-job creation, and target-channel publication.

## Steps

1. Add tests that prove startup recovery picks up persisted `pending` rows.
2. Add tests that prove stale rows short-circuit before filter evaluation.
3. Add tests that prove fresh rows persist normalized text, classification results, and candidate handoff state.
4. Keep the verification surface focused on the classification pipeline and not later event or publish workflows.

## Risks

- Without verification, stale-ordering or recovery regressions can slip in quietly.
- If tests broaden into later M2 or M3 workflows, this task will start reowning contracts that belong elsewhere.

## Acceptance Criteria

- Startup recovery for persisted `pending` rows is covered by automated tests.
- Stale short-circuit behavior is covered by automated tests.
- Fresh classification and candidate handoff behavior are covered by automated tests.
- The task stays focused on the classification pipeline contract.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Candidate classification pipeline](../0028_candidate_classification_pipeline.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0041_processing_worker_wiring_and_startup_recovery.md](01_0041_processing_worker_wiring_and_startup_recovery.md)
- Depends on task: [02_0042_stale_message_short_circuit.md](02_0042_stale_message_short_circuit.md)
- Depends on task: [03_0043_fresh_row_normalization_and_filter_classification.md](03_0043_fresh_row_normalization_and_filter_classification.md)
- Depends on task: [04_0044_candidate_metadata_and_aggregation_handoff.md](04_0044_candidate_metadata_and_aggregation_handoff.md)
