# M1 Intake state contract alignment: migration and readiness contract alignment

Planning ID: 0031
Status: Draft
Last updated: 2026-04-06

## Goal

Align database migrations and readiness checks with the canonical M1 storage contract so the renamed tables and split status model stay verifiable at startup.

## Scope

- Update the Alembic migration path needed for the canonical `tg_message` and `event` contract.
- Keep startup readiness checks queryable against the renamed tables and relation names.
- Verify the database contract after the table rename, relation rename, and split status model change.
- Exclude repository redesign, reader behavior, filter evaluation, and processing or publication logic.

## Steps

1. Update the migration path so the canonical M1 schema can be created or upgraded without legacy `message_records` and `event_records` names.
2. Refresh readiness checks to query the renamed tables and canonical relation names.
3. Verify that the split status model remains queryable after the migration work lands.
4. Keep the migration and readiness contract aligned with the canonical storage metadata from the first task.

## Risks

- A partial rename that updates tables but not constraint or index names will leave the schema contract inconsistent.
- If readiness checks lag behind the migration contract, startup can report false failures or false success.
- Mixing repository behavior into this task would blur the boundary between storage contract alignment and runtime usage.

## Acceptance Criteria

- The migration path brings the database to the canonical `tg_message` and `event` contract.
- Readiness checks operate against the renamed tables and relation names.
- The split status model remains queryable and verifiable after startup.
- Migration and readiness coverage no longer depends on legacy `message_records` or `event_records` naming.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Intake state contract alignment](../0025_intake_state_contract_alignment.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0029_canonical_schema_metadata_and_relation_surface.md](01_0029_canonical_schema_metadata_and_relation_surface.md)
- Depends on task: [02_0030_storage_facade_and_repository_boundary_update.md](02_0030_storage_facade_and_repository_boundary_update.md)
- Depends on task: [02_0017_startup_readiness_hooks.md](../../../01_0001_foundations_ready/04_0015_storage_contract_readiness/tasks/02_0017_startup_readiness_hooks.md)
