# M1 Candidate classification pipeline

Planning ID: 0028
Status: Draft
Last updated: 2026-04-06

## Goal

Turn persisted intake rows into durable `outdated`, `filtered_out`, or `candidate` state through the processing queue, persist processing-owned `normalized_text` and typed match metadata, and stop at the aggregation handoff boundary without starting event or publish behavior.

## Scope

- Implement the processing worker that consumes queued `tg_message` identifiers, recovers persisted `pending` rows on startup, and loads the persisted intake record before classification.
- Apply the explicit stale-message rule before any filter evaluation.
- Compute and persist processing-owned `normalized_text` for fresh rows before filter classification.
- Persist `classification_status='outdated'` for stale rows without filter or candidate processing.
- Persist `classification_status='filtered_out'` or `classification_status='candidate'` for fresh rows, and capture `event_type` and `event_signal` for candidates.
- Mark candidate rows with `aggregation_status='queued'` as the only durable handoff into later M2 and M3 aggregation work.
- Exclude candidate signature generation, event creation, duplicate suppression, `clear` lifecycle handling, publish-job creation, and target-channel publication.

## Steps

1. Implement [M1 Candidate classification pipeline: processing worker wiring and startup recovery](tasks/01_0041_processing_worker_wiring_and_startup_recovery.md) to attach the processing worker to the canonical runtime queue boundary and recover persisted `pending` rows on startup.
2. Implement [M1 Candidate classification pipeline: stale-message short-circuit](tasks/02_0042_stale_message_short_circuit.md) to load each queued or recovered `tg_message` row and mark rows older than `classification_stale_after_seconds` as `outdated` before any filter work.
3. Implement [M1 Candidate classification pipeline: fresh-row normalization and filter classification](tasks/03_0043_fresh_row_normalization_and_filter_classification.md) to compute processing-owned `normalized_text` for fresh rows and persist either `filtered_out` or `candidate` with typed match metadata.
4. Implement [M1 Candidate classification pipeline: candidate metadata and aggregation handoff](tasks/04_0044_candidate_metadata_and_aggregation_handoff.md) to persist `event_type` and `event_signal` for candidates and transition them to `aggregation_status='queued'`.
5. Finish with [M1 Candidate classification pipeline: classification pipeline verification](tasks/05_0045_classification_pipeline_verification.md) to protect queue recovery, stale handling, fresh classification, and aggregation handoff with focused tests.

## Risks

- If the stale check runs after filter evaluation, M1 will violate the delivery-plan rule that stale rows never enter filter or candidate processing.
- Leaving `normalized_text` ownership ambiguous between the reader and processing worker can cause M1 classification and M2 event deduplication to diverge.
- Building `candidate_signature` inside M1 would split ownership between intake classification and later event deduplication.
- Missing startup recovery for persisted `pending` rows can leave durable intake work stranded after a restart.
- Starting even a minimal event or publish path here would blur the M1/M2 milestone boundary and make later acceptance hard to reason about.

## Acceptance Criteria

- Queue-driven intake and processing run end-to-end without publication, and startup recovery picks up persisted `pending` rows left behind before classification.
- Messages already stale before classification are marked `outdated` without filter or candidate processing.
- Fresh rows persist processing-owned `normalized_text` before filter classification and then become either `filtered_out` or `candidate` based on the documented filter engine.
- Candidate classification persists `event_type` and `event_signal` for matched rows.
- Candidate rows transition to `aggregation_status='queued'` and stop there until later aggregation stories build `candidate_signature` from persisted `normalized_text` and consume them.

## Links

- Parent epic: [M1 Intake To Candidate](../0024_intake_to_candidate.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
- Depends on story: [M1 Source intake and message deduplication](../02_0026_source_intake_and_message_deduplication/0026_source_intake_and_message_deduplication.md)
- Depends on story: [M1 Normalization and filter engine](../03_0027_normalization_and_filter_engine/0027_normalization_and_filter_engine.md)
- Depends on story: [M0 Bootstrap, observability, and test harness](../../01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md)
