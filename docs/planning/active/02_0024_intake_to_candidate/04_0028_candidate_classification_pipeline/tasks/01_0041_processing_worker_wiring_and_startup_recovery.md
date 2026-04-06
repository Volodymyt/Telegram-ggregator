# M1 Candidate classification pipeline: processing worker wiring and startup recovery

Planning ID: 0041
Status: Draft
Last updated: 2026-04-06

## Goal

Attach the processing worker to the canonical runtime queue boundary and recover persisted `pending` intake rows on startup so M1 classification can resume from durable state.

## Scope

- Wire the processing worker into the canonical runtime queue boundary introduced in M0.
- Add a startup recovery scan for persisted `tg_message` rows still in `classification_status='pending'`.
- Keep the worker wiring thin and separate from stale handling, filter evaluation, and aggregation handoff.
- Exclude candidate signature generation, event creation or deduplication, `clear` lifecycle handling, publish-job creation, and target-channel publication.

## Steps

1. Register the processing worker with the canonical runtime queue boundary used by later M1 execution.
2. Add startup recovery for persisted `pending` rows so classification work can resume after a restart.
3. Keep worker bootstrap focused on durable queue ownership and recovery without embedding classification rules.

## Risks

- If the worker is not attached to the canonical queue boundary, later classification work will drift from the shared runtime contract.
- Missing startup recovery would leave persisted intake rows stranded after process restarts.
- Pulling stale handling or filter evaluation into bootstrap would blur the ownership line between runtime wiring and classification logic.

## Acceptance Criteria

- The processing worker runs through the canonical runtime queue boundary.
- Startup recovery finds persisted `pending` `tg_message` rows.
- Worker wiring stays thin and does not absorb stale, filter, aggregation, or publish behavior.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Candidate classification pipeline](../0028_candidate_classification_pipeline.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on story: [M1 Source intake and message deduplication](../../02_0026_source_intake_and_message_deduplication/0026_source_intake_and_message_deduplication.md)
- Depends on story: [M0 Bootstrap, observability, and test harness](../../../01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
