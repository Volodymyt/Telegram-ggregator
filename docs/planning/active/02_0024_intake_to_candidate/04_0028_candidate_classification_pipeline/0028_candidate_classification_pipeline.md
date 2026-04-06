# M1 Candidate classification pipeline

Planning ID: 0028
Status: Draft
Last updated: 2026-04-06

## Goal

Turn persisted intake rows into durable `outdated`, `filtered_out`, or `candidate` state through the processing queue, and stop at the aggregation handoff boundary without starting event or publish behavior.

## Scope

- Implement the processing worker that consumes queued `tg_message` identifiers and loads the persisted intake record before classification.
- Apply the explicit stale-message rule before any filter evaluation.
- Persist `classification_status='outdated'` for stale rows without filter or candidate processing.
- Persist `classification_status='filtered_out'` or `classification_status='candidate'` for fresh rows, and capture `event_type`, `event_signal`, and `candidate_signature` for candidates.
- Mark candidate rows with `aggregation_status='queued'` as the only durable handoff into later M2 and M3 aggregation work.
- Exclude event creation, duplicate suppression, `clear` lifecycle handling, publish-job creation, and target-channel publication.

## Steps

1. Wire the processing worker into the canonical runtime queue boundary introduced in M0.
2. Load each queued `tg_message` row from storage and short-circuit to `outdated` when the row is older than `classification_stale_after_seconds`.
3. For fresh rows, apply the filter engine and persist either `filtered_out` or `candidate` with the typed match metadata.
4. Build `candidate_signature` from normalized text after stripping URLs, usernames, punctuation, and repeated whitespace, then persist `aggregation_status='queued'` for later aggregation.

## Risks

- If the stale check runs after filter evaluation, M1 will violate the delivery-plan rule that stale rows never enter filter or candidate processing.
- Persisting `candidate_signature` anywhere other than the processing handoff can split ownership between M1 and later aggregation stories.
- Starting even a minimal event or publish path here would blur the M1/M2 milestone boundary and make later acceptance hard to reason about.

## Acceptance Criteria

- Queue-driven intake and processing run end-to-end without publication.
- Messages already stale before classification are marked `outdated` without filter or candidate processing.
- Fresh rows become either `filtered_out` or `candidate` based on the documented filter engine.
- Candidate classification persists `event_type`, `event_signal`, and `candidate_signature`.
- Candidate rows transition to `aggregation_status='queued'` and stop there until later aggregation stories consume them.

## Links

- Parent epic: [M1 Intake To Candidate](../0024_intake_to_candidate.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
- Depends on story: [M1 Source intake and message deduplication](../02_0026_source_intake_and_message_deduplication/0026_source_intake_and_message_deduplication.md)
- Depends on story: [M1 Normalization and filter engine](../03_0027_normalization_and_filter_engine/0027_normalization_and_filter_engine.md)
- Depends on story: [M0 Bootstrap, observability, and test harness](../../01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md)
