# Story 0025 Storage Contract Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish story `0025` by aligning storage metadata, migrations, readiness, tests, and planning statuses with the canonical `tg_message` and `event` contract.

**Architecture:** Keep the edited `0001` Alembic revision as the canonical baseline already present in this branch. Add only new schema deltas after `0001`, remove the extra schema smoke readiness query, and let automated tests own contract verification.

**Tech Stack:** Python 3.12, SQLAlchemy Core, Alembic, pytest, pytest-asyncio.

---

## File Structure

- Modify `src/telegram_aggregator/storage/tables.py`: canonical status sets and SQLAlchemy status column types.
- Create `alembic/versions/0002_status_columns_varchar_32.py`: new migration that changes status columns from `TEXT` to `VARCHAR(32)`.
- Modify `src/telegram_aggregator/storage/readiness.py`: remove `check_schema_queryable`; keep reachability and Alembic-current checks.
- Modify `src/telegram_aggregator/storage/__init__.py`: remove `check_schema_queryable` export; keep canonical `event` and `tg_message` exports.
- Replace `tests/unit/test_schema_baseline.py`: assert canonical table names, status columns, status sets, indexes, foreign keys, and revision chain.
- Modify `tests/unit/test_storage_surface.py`: assert canonical public API, canonical repository parameters, and readiness call flow.
- Modify these planning files only after tests pass:
  - `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md`
  - `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/01_0029_canonical_schema_metadata_and_relation_surface.md`
  - `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/02_0030_storage_facade_and_repository_boundary_update.md`
  - `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/03_0031_migration_and_readiness_contract_alignment.md`
  - `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/04_0032_verification_and_reference_cleanup.md`

Do not edit `docs_ua/**` or `**/brief.uk.md`; those paths are ignored by project instructions.

---

### Task 1: Schema Metadata And Alembic Type Migration

**Files:**
- Modify: `tests/unit/test_schema_baseline.py`
- Modify: `src/telegram_aggregator/storage/tables.py`
- Create: `alembic/versions/0002_status_columns_varchar_32.py`

- [ ] **Step 1: Replace schema baseline tests with canonical storage contract tests**

Replace `tests/unit/test_schema_baseline.py` with:

```python
from __future__ import annotations

import ast
from pathlib import Path

import pytest
from sqlalchemy import String, Table


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERSIONS_DIR = PROJECT_ROOT / "alembic" / "versions"


def _read_revision(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    values: dict[str, object] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id in {"revision", "down_revision"}:
                assert isinstance(node.value, ast.Constant)
                values[node.target.id] = node.value.value
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"revision", "down_revision"}:
                    assert isinstance(node.value, ast.Constant)
                    values[target.id] = node.value.value

    return values


def test_tables_module_importable() -> None:
    import telegram_aggregator.storage.tables  # noqa: F401


def test_tables_exported_from_storage_package() -> None:
    from telegram_aggregator.storage import event, tg_message

    assert event is not None
    assert tg_message is not None


def test_canonical_tables_registered_in_metadata() -> None:
    from telegram_aggregator.storage import metadata

    assert "tg_message" in metadata.tables
    assert "event" in metadata.tables
    assert "message_records" not in metadata.tables
    assert "event_records" not in metadata.tables


def test_tables_are_sqlalchemy_table_instances() -> None:
    from telegram_aggregator.storage import event, tg_message

    assert isinstance(tg_message, Table)
    assert isinstance(event, Table)


@pytest.mark.parametrize(
    "column_name",
    [
        "id",
        "source_chat_id",
        "source_message_id",
        "source_title",
        "source_link",
        "raw_text",
        "normalized_text",
        "has_media",
        "event_type",
        "event_signal",
        "candidate_signature",
        "event_id",
        "classification_status",
        "aggregation_status",
        "publish_status",
        "filter_reason",
        "target_message_id",
        "publish_attempts",
        "last_error",
        "received_at",
        "updated_at",
    ],
)
def test_tg_message_has_column(column_name: str) -> None:
    from telegram_aggregator.storage import tg_message

    assert column_name in tg_message.c, f"tg_message missing column: {column_name!r}"


@pytest.mark.parametrize(
    "column_name",
    [
        "id",
        "target_channel",
        "event_type",
        "state",
        "started_at",
        "last_seen_at",
        "ended_at",
        "canonical_message_id",
        "published_target_message_id",
        "publish_status",
        "created_at",
        "updated_at",
    ],
)
def test_event_has_column(column_name: str) -> None:
    from telegram_aggregator.storage import event

    assert column_name in event.c, f"event missing column: {column_name!r}"


@pytest.mark.parametrize(
    "column_name",
    [
        "source_chat_id",
        "source_message_id",
        "has_media",
        "classification_status",
        "aggregation_status",
        "publish_status",
        "publish_attempts",
        "received_at",
        "updated_at",
    ],
)
def test_tg_message_required_columns_not_nullable(column_name: str) -> None:
    from telegram_aggregator.storage import tg_message

    assert not tg_message.c[column_name].nullable


@pytest.mark.parametrize(
    "column_name",
    [
        "source_title",
        "source_link",
        "raw_text",
        "normalized_text",
        "event_type",
        "event_signal",
        "candidate_signature",
        "event_id",
        "filter_reason",
        "target_message_id",
        "last_error",
    ],
)
def test_tg_message_optional_columns_are_nullable(column_name: str) -> None:
    from telegram_aggregator.storage import tg_message

    assert tg_message.c[column_name].nullable


def test_event_ended_at_is_nullable() -> None:
    from telegram_aggregator.storage import event

    assert event.c["ended_at"].nullable


def test_event_required_columns_not_nullable() -> None:
    from telegram_aggregator.storage import event

    for column_name in (
        "target_channel",
        "event_type",
        "state",
        "started_at",
        "last_seen_at",
        "publish_status",
        "created_at",
        "updated_at",
    ):
        assert not event.c[column_name].nullable


def test_status_columns_are_varchar_32() -> None:
    from telegram_aggregator.storage import event, tg_message

    status_columns = (
        event.c.publish_status,
        tg_message.c.classification_status,
        tg_message.c.aggregation_status,
        tg_message.c.publish_status,
    )

    for column in status_columns:
        assert isinstance(column.type, String)
        assert column.type.length == 32


def test_status_value_sets_match_delivery_plan() -> None:
    from telegram_aggregator.storage.tables import (
        AGGREGATION_STATUSES,
        CLASSIFICATION_STATUSES,
        EVENT_PUBLISH_STATUSES,
        EVENT_STATES,
        MESSAGE_PUBLISH_STATUSES,
    )

    assert CLASSIFICATION_STATUSES == (
        "pending",
        "outdated",
        "filtered_out",
        "candidate",
    )
    assert AGGREGATION_STATUSES == (
        "new",
        "queued",
        "suppressed_duplicate",
        "selected",
        "clear_processed",
        "orphan_clear",
    )
    assert MESSAGE_PUBLISH_STATUSES == (
        "new",
        "queued",
        "publishing",
        "published",
        "failed",
    )
    assert EVENT_STATES == ("open", "closed")
    assert EVENT_PUBLISH_STATUSES == ("pending", "published", "failed")


def test_tg_message_has_unique_constraint_on_source_ids() -> None:
    from telegram_aggregator.storage import tg_message

    unique_constraints = [
        constraint
        for constraint in tg_message.constraints
        if hasattr(constraint, "columns")
        and {column.name for column in constraint.columns}
        == {"source_chat_id", "source_message_id"}
    ]

    assert unique_constraints
    assert unique_constraints[0].name == "uq_tg_message_source_chat_id_source_message_id"


def test_tg_message_has_classification_status_index() -> None:
    from telegram_aggregator.storage import tg_message

    indexes = {
        index.name: tuple(column.name for column in index.columns)
        for index in tg_message.indexes
    }

    assert indexes["ix_tg_message_classification_status"] == ("classification_status",)


def test_tg_message_has_event_type_classification_received_index() -> None:
    from telegram_aggregator.storage import tg_message

    indexes = {
        index.name: tuple(column.name for column in index.columns)
        for index in tg_message.indexes
    }

    assert indexes["ix_tg_message_event_type_classification_status_received_at"] == (
        "event_type",
        "classification_status",
        "received_at",
    )


def test_tg_message_event_id_has_foreign_key_to_event() -> None:
    from telegram_aggregator.storage import tg_message

    column = tg_message.c.event_id
    assert column.foreign_keys

    fk = next(iter(column.foreign_keys))
    assert fk.column.table.name == "event"
    assert fk.column.name == "id"
    assert fk.constraint.name == "fk_tg_message_event_id_event"


def test_legacy_storage_names_not_exported() -> None:
    import telegram_aggregator.storage as storage

    assert not hasattr(storage, "message_records")
    assert not hasattr(storage, "event_records")


def test_alembic_versions_exist() -> None:
    revision_files = sorted(VERSIONS_DIR.glob("*.py"))

    assert {path.name for path in revision_files} >= {
        "0001_baseline_schema.py",
        "0002_status_columns_varchar_32.py",
    }


def test_baseline_revision_has_no_down_revision() -> None:
    values = _read_revision(VERSIONS_DIR / "0001_baseline_schema.py")

    assert values["revision"] == "0001"
    assert values["down_revision"] is None


def test_status_column_type_revision_points_to_baseline() -> None:
    values = _read_revision(VERSIONS_DIR / "0002_status_columns_varchar_32.py")

    assert values["revision"] == "0002"
    assert values["down_revision"] == "0001"
```

- [ ] **Step 2: Run schema tests and verify they expose current gaps**

Run:

```bash
pytest tests/unit/test_schema_baseline.py -q
```

Expected: FAIL because status columns are still `Text`, `AGGREGATION_STATUSES` lacks `clear_processed` and `orphan_clear`, and `0002_status_columns_varchar_32.py` does not exist yet.

- [ ] **Step 3: Update storage metadata status sets and status column types**

In `src/telegram_aggregator/storage/tables.py`, update `AGGREGATION_STATUSES` to:

```python
AGGREGATION_STATUSES = (
    "new",
    "queued",
    "suppressed_duplicate",
    "selected",
    "clear_processed",
    "orphan_clear",
)
```

In the `event` table, replace the `publish_status` column with:

```python
    sa.Column("publish_status", sa.String(32), nullable=False, server_default="pending"),
```

In the `tg_message` table, replace the three status columns with:

```python
    sa.Column(
        "classification_status",
        sa.String(32),
        nullable=False,
        server_default="pending",
    ),
    sa.Column(
        "aggregation_status",
        sa.String(32),
        nullable=False,
        server_default="new",
    ),
    sa.Column("publish_status", sa.String(32), nullable=False, server_default="new"),
```

- [ ] **Step 4: Add the Alembic status column type migration**

Create `alembic/versions/0002_status_columns_varchar_32.py`:

```python
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STATUS_COLUMNS = (
    ("event", "publish_status"),
    ("tg_message", "classification_status"),
    ("tg_message", "aggregation_status"),
    ("tg_message", "publish_status"),
)


def upgrade() -> None:
    for table_name, column_name in STATUS_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.Text(),
            type_=sa.String(32),
            existing_nullable=False,
        )


def downgrade() -> None:
    for table_name, column_name in STATUS_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.String(32),
            type_=sa.Text(),
            existing_nullable=False,
        )
```

- [ ] **Step 5: Run schema tests and verify they pass**

Run:

```bash
pytest tests/unit/test_schema_baseline.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit schema and migration changes**

Run:

```bash
git add tests/unit/test_schema_baseline.py src/telegram_aggregator/storage/tables.py alembic/versions/0002_status_columns_varchar_32.py
git commit -m "fix: align story 0025 schema contract tests"
```

---

### Task 2: Storage Surface Contract And Readiness Cleanup

**Files:**
- Modify: `tests/unit/test_storage_surface.py`
- Modify: `src/telegram_aggregator/storage/readiness.py`
- Modify: `src/telegram_aggregator/storage/__init__.py`

- [ ] **Step 1: Update storage surface imports for signature assertions**

Add this import near the top of `tests/unit/test_storage_surface.py`:

```python
import inspect
```

- [ ] **Step 2: Update public API assertions to reject legacy and schema-queryable exports**

In `tests/unit/test_storage_surface.py`, add these assertions to `test_storage_public_api` after the existing storage error assertions:

```python
    assert hasattr(storage, "tg_message"), "tg_message missing from public API"
    assert hasattr(storage, "event"), "event missing from public API"
    assert hasattr(storage, "check_storage_readiness"), "check_storage_readiness missing from public API"
    assert hasattr(storage, "check_db_reachable"), "check_db_reachable missing from public API"
    assert hasattr(storage, "check_migrations_current"), "check_migrations_current missing from public API"
    assert not hasattr(storage, "message_records"), "legacy message_records must not be exported"
    assert not hasattr(storage, "event_records"), "legacy event_records must not be exported"
    assert not hasattr(storage, "check_schema_queryable"), "schema smoke check must not be exported"
```

- [ ] **Step 3: Add repository signature assertions for canonical names**

Add this test after `test_event_repository_exposes_crud_methods`:

```python
def test_repository_update_signatures_use_canonical_storage_names() -> None:
    from telegram_aggregator.storage import EventRepository, MessageRepository

    message_params = inspect.signature(
        MessageRepository.update_message_status
    ).parameters
    event_params = inspect.signature(EventRepository.update_event).parameters

    for name in (
        "classification_status",
        "aggregation_status",
        "publish_status",
        "event_id",
    ):
        assert name in message_params

    assert "status" not in message_params
    assert "event_record_id" not in message_params
    assert "canonical_message_id" in event_params
    assert "canonical_message_record_id" not in event_params
```

- [ ] **Step 4: Add a focused readiness module test for removed schema query helper**

Add this test after `test_readiness_rejects_cwd_without_alembic_directory`:

```python
def test_readiness_module_does_not_expose_schema_queryable_check() -> None:
    import telegram_aggregator.storage.readiness as readiness

    assert not hasattr(readiness, "check_schema_queryable")
```

- [ ] **Step 5: Replace the legacy message update test with canonical assertions**

Replace `test_message_repository_update_message_status_filters_out_none_values` with:

```python
@pytest.mark.asyncio
async def test_message_repository_update_message_status_filters_out_none_values() -> None:
    from telegram_aggregator.storage import MessageRepository

    conn = _RecordingConnection(
        row={
            "id": 11,
            "classification_status": "candidate",
            "aggregation_status": "queued",
            "event_id": 7,
            "event_type": "ballistic",
        }
    )
    repo = MessageRepository(conn=conn)  # type: ignore[arg-type]

    result = await repo.update_message_status(
        message_id=11,
        classification_status="candidate",
        aggregation_status="queued",
        publish_status=None,
        filter_reason=None,
        event_id=7,
        normalized_text=None,
        event_type="ballistic",
        event_signal=None,
        candidate_signature=None,
    )

    assert result == {
        "id": 11,
        "classification_status": "candidate",
        "aggregation_status": "queued",
        "event_id": 7,
        "event_type": "ballistic",
    }
    assert len(conn.executed) == 1

    stmt = conn.executed[0]
    params = stmt.compile().params

    assert params["id_1"] == 11
    assert params["classification_status"] == "candidate"
    assert params["aggregation_status"] == "queued"
    assert params["event_id"] == 7
    assert params["event_type"] == "ballistic"
    assert "publish_status" not in params
    assert "filter_reason" not in params
    assert "normalized_text" not in params
    assert "event_signal" not in params
    assert "candidate_signature" not in params
    assert set(params) == {
        "id_1",
        "classification_status",
        "aggregation_status",
        "event_id",
        "event_type",
    }
```

- [ ] **Step 6: Add an event repository canonical message field test**

Add this test after `test_event_repository_update_event_filters_out_none_values`:

```python
@pytest.mark.asyncio
async def test_event_repository_update_event_uses_canonical_message_id() -> None:
    from telegram_aggregator.storage import EventRepository

    conn = _RecordingConnection(
        row={
            "id": 7,
            "canonical_message_id": 11,
        }
    )
    repo = EventRepository(conn=conn)  # type: ignore[arg-type]

    result = await repo.update_event(event_id=7, canonical_message_id=11)

    assert result == {
        "id": 7,
        "canonical_message_id": 11,
    }
    assert len(conn.executed) == 1

    stmt = conn.executed[0]
    params = stmt.compile().params

    assert params["id_1"] == 7
    assert params["canonical_message_id"] == 11
    assert "canonical_message_record_id" not in params
    assert set(params) == {"id_1", "canonical_message_id"}
```

- [ ] **Step 7: Run storage surface tests and verify readiness cleanup is still missing**

Run:

```bash
pytest tests/unit/test_storage_surface.py -q
```

Expected: FAIL because `check_schema_queryable` still exists, is exported, and is still called by `check_storage_readiness`.

- [ ] **Step 8: Remove `check_schema_queryable` from readiness**

In `src/telegram_aggregator/storage/readiness.py`, delete the full `check_schema_queryable` function and change `check_storage_readiness` to:

```python
async def check_storage_readiness(engine: AsyncEngine) -> ReadinessResult:
    await check_db_reachable(engine)
    await check_migrations_current(engine)
    return ReadinessResult(db_reachable=True, migrations_current=True)
```

- [ ] **Step 9: Remove `check_schema_queryable` from package exports**

In `src/telegram_aggregator/storage/__init__.py`, replace the readiness import block with:

```python
from telegram_aggregator.storage.readiness import (
    check_storage_readiness,
    check_db_reachable,
    check_migrations_current,
    ReadinessResult,
)
```

In the `__all__` list, remove this entry:

```python
    "check_schema_queryable",
```

- [ ] **Step 10: Run the full storage surface test file**

Run:

```bash
pytest tests/unit/test_storage_surface.py -q
```

Expected: PASS.

- [ ] **Step 11: Commit storage surface and readiness cleanup**

Run:

```bash
git add tests/unit/test_storage_surface.py src/telegram_aggregator/storage/readiness.py src/telegram_aggregator/storage/__init__.py
git commit -m "fix: align storage surface readiness contract"
```

---

### Task 3: Planning Status Closure

**Files:**
- Modify: `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md`
- Modify: `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/01_0029_canonical_schema_metadata_and_relation_surface.md`
- Modify: `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/02_0030_storage_facade_and_repository_boundary_update.md`
- Modify: `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/03_0031_migration_and_readiness_contract_alignment.md`
- Modify: `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/04_0032_verification_and_reference_cleanup.md`

- [ ] **Step 1: Run targeted verification before changing planning status**

Run:

```bash
pytest tests/unit/test_schema_baseline.py tests/unit/test_storage_surface.py -q
```

Expected: PASS.

- [ ] **Step 2: Update the parent story status**

In `docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md`, change:

```markdown
Status: Draft
Last updated: 2026-04-06
```

to:

```markdown
Status: Done
Last updated: 2026-05-02
```

- [ ] **Step 3: Update nested task statuses**

In each nested task file listed for this task, change the header from:

```markdown
Status: Draft
Last updated: 2026-04-06
```

to:

```markdown
Status: Done
Last updated: 2026-05-02
```

- [ ] **Step 4: Verify planning lookup sees the story as done**

Run:

```bash
bin/find-planning-item 0025
```

Expected output includes:

```text
Planning ID: 0025
Status: Done
```

- [ ] **Step 5: Verify nested task statuses**

Run:

```bash
rg -n 'Planning ID: 00(25|29|30|31|32)|Status: ' docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment
```

Expected: each file for `0025`, `0029`, `0030`, `0031`, and `0032` shows `Status: Done`.

- [ ] **Step 6: Commit planning status closure**

Run:

```bash
git add docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/01_0029_canonical_schema_metadata_and_relation_surface.md docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/02_0030_storage_facade_and_repository_boundary_update.md docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/03_0031_migration_and_readiness_contract_alignment.md docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment/tasks/04_0032_verification_and_reference_cleanup.md
git commit -m "docs: mark story 0025 storage alignment done"
```

---

### Task 4: Full Verification

**Files:**
- No planned file edits.

- [ ] **Step 1: Run the full unit test suite**

Run:

```bash
pytest
```

Expected: PASS.

- [ ] **Step 2: Verify removed readiness helper is gone**

Run:

```bash
rg -n --glob '!docs_ua/**' --glob '!**/brief.uk.md' 'check_schema_queryable' src tests alembic docs/planning/active/02_0024_intake_to_candidate/01_0025_intake_state_contract_alignment
```

Expected: no matches.

- [ ] **Step 3: Verify legacy storage names are absent from active code and storage tests**

Run:

```bash
rg -n 'message_records|event_records|event_record_id|canonical_message_record_id' src/telegram_aggregator/storage tests/unit/test_schema_baseline.py tests/unit/test_storage_surface.py alembic/versions
```

Expected: no matches.

- [ ] **Step 4: Verify working tree state**

Run:

```bash
git status --short
```

Expected: no unstaged or uncommitted changes.
