# Story 0025 Storage Contract Fixes Design

## Context

Story `0025` aligns the storage contract from the legacy
`message_records` and `event_records` model to the canonical `tg_message`
and `event` model. The current branch already updates the baseline Alembic
revision `0001` to create the canonical tables. That edited baseline remains
as-is.

All further schema changes for this fix set must be represented by new Alembic
revisions after `0001`.

## Goals

- Fix the review findings for story `0025` and its nested tasks `0029`,
  `0030`, `0031`, and `0032`.
- Remove `check_schema_queryable` from the readiness contract.
- Change status columns from unbounded text to `varchar(32)` in code metadata
  and through a new Alembic migration.
- Update tests to assert the canonical storage contract instead of the legacy
  names.
- Mark the story and nested tasks done only after verification passes.

## Non-Goals

- Do not rewrite `0001` further.
- Do not add a migration path from the original legacy `0001` schema to the
  edited canonical `0001` baseline.
- Do not add compatibility aliases for `message_records`, `event_records`, or
  `event_record_id`.
- Do not implement intake, filtering, aggregation, or publish behavior.

## Schema Design

The storage metadata remains centered on `event` and `tg_message`.

The following columns become `String(32)` in SQLAlchemy metadata and
`VARCHAR(32)` in the database:

- `event.publish_status`
- `tg_message.classification_status`
- `tg_message.aggregation_status`
- `tg_message.publish_status`

`AGGREGATION_STATUSES` must include the complete locked set from the delivery
plan:

- `new`
- `queued`
- `suppressed_duplicate`
- `selected`
- `clear_processed`
- `orphan_clear`

The canonical relationship remains `tg_message.event_id -> event.id`.

## Migration Design

Add a new Alembic revision after `0001`, for example
`0002_status_columns_varchar_32.py`.

The migration upgrades the four status columns from `TEXT` to `VARCHAR(32)`.
The downgrade returns those columns to `TEXT`.

The edited `0001` stays untouched during implementation. It remains the
canonical baseline already present in this branch.

## Readiness Design

Remove `check_schema_queryable` entirely.

`check_storage_readiness` should call only:

- `check_db_reachable`
- `check_migrations_current`

This keeps readiness focused on reachability and Alembic state. Schema contract
coverage belongs in migrations and tests, not in an extra hard-coded startup
query.

## Repository Design

Repository APIs stay canonical:

- Message updates use `classification_status`, `aggregation_status`,
  `publish_status`, and `event_id`.
- Event updates use `canonical_message_id` and `publish_status`.
- No legacy `status`, `event_record_id`, or `canonical_message_record_id`
  surface remains in the storage package.

## Test Design

Update `tests/unit/test_schema_baseline.py` to assert:

- `tg_message` and `event` are exported from the storage package.
- canonical table names are registered in metadata.
- canonical columns exist, including split message statuses and `event_id`.
- status columns use `String(32)`.
- idempotent source-message uniqueness remains on
  `(source_chat_id, source_message_id)`.
- canonical indexes and foreign key names do not use legacy naming.

Update `tests/unit/test_storage_surface.py` to assert:

- message repository update calls use the canonical status and relation
  parameters.
- readiness no longer calls or exports `check_schema_queryable`.
- storage package exports match the canonical contract.

Add or update Alembic tests so the version set includes the new `0002`
revision and its `down_revision` points to `0001`.

## Planning Status Design

After implementation and verification pass, update planning status to `Done`
for:

- story `0025`
- task `0029`
- task `0030`
- task `0031`
- task `0032`

Do not change unrelated story trees or ignored translation files.

## Verification

Run the unit test suite with:

```bash
pytest
```

The implementation is complete only when the suite passes and no legacy
storage names remain in active code or storage tests.
