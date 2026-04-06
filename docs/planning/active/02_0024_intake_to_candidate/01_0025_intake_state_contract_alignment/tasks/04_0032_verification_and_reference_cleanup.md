# M1 Intake state contract alignment: verification and reference cleanup

Planning ID: 0032
Status: Draft
Last updated: 2026-04-06

## Goal

Protect the realigned storage contract with focused verification and remove legacy planning references inside this story tree.

## Scope

- Add storage-focused tests for the canonical schema metadata, repository boundary, and migration/readiness contract.
- Refresh this story's planning references so they no longer describe the old `message_records`, `event_records`, or `event_record_id` contract.
- Keep the task focused on verification and story-tree cleanup rather than new runtime behavior.
- Exclude Telegram intake, filter evaluation, candidate claiming, event deduplication, and publication work.

## Steps

1. Add focused tests that assert the canonical schema metadata and relation surface.
2. Add verification for the storage facade and migration/readiness contract where the existing test harness already exercises those boundaries.
3. Update the parent story references in this story tree so the steps and acceptance language describe the canonical M1 contract.
4. Confirm the story tree no longer depends on legacy storage naming in its own planning docs.

## Risks

- If verification only checks happy paths, later stories can still regress on legacy naming or status-field shape.
- Cleanup that touches planning docs without matching tests can hide unresolved storage drift.
- This task can become too broad if it tries to reimplement migration or repository work instead of verifying it.

## Acceptance Criteria

- Tests cover the canonical schema metadata, repository boundary, and migration/readiness contract at the level owned by this story.
- This story tree no longer describes the storage contract with `message_records`, `event_records`, or `event_record_id`.
- The cleanup stays limited to planning references and verification, without adding new business behavior.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Intake state contract alignment](../0025_intake_state_contract_alignment.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0029_canonical_schema_metadata_and_relation_surface.md](01_0029_canonical_schema_metadata_and_relation_surface.md)
- Depends on task: [02_0030_storage_facade_and_repository_boundary_update.md](02_0030_storage_facade_and_repository_boundary_update.md)
- Depends on task: [03_0031_migration_and_readiness_contract_alignment.md](03_0031_migration_and_readiness_contract_alignment.md)
