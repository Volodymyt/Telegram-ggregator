# M1 Candidate classification pipeline: stale-message short-circuit

Planning ID: 0042
Status: Draft
Last updated: 2026-04-06

## Goal

Short-circuit stale intake rows before any filter work so M1 never classifies rows that are already outside the operator-defined freshness window.

## Scope

- Load each queued or recovered `tg_message` row from storage before classification.
- Apply the explicit stale-message rule before any filter evaluation.
- Mark rows older than `classification_stale_after_seconds` as `outdated`.
- Exclude filter evaluation, normalized-text persistence for fresh rows, candidate metadata handling, event creation or deduplication, and publication.

## Steps

1. Load queued or recovered `tg_message` rows from storage for classification.
2. Compare row age to `classification_stale_after_seconds` before any filter work.
3. Persist `classification_status='outdated'` for stale rows and stop processing them.

## Risks

- If the stale check runs after filter evaluation, M1 will violate the delivery-plan rule that stale rows never enter candidate processing.
- Implementing the stale rule as an implicit constant would hide an operator-facing runtime decision.
- Letting this task absorb fresh-row classification would create overlap with the following task.

## Acceptance Criteria

- Stale rows are detected before filter evaluation.
- Rows older than `classification_stale_after_seconds` are marked `outdated`.
- Stale handling stops without entering fresh-row normalization or aggregation handoff logic.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Candidate classification pipeline](../0028_candidate_classification_pipeline.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0041_processing_worker_wiring_and_startup_recovery.md](01_0041_processing_worker_wiring_and_startup_recovery.md)
- Depends on story: [M1 Normalization and filter engine](../../03_0027_normalization_and_filter_engine/0027_normalization_and_filter_engine.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
