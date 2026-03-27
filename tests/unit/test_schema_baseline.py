from __future__ import annotations

import pytest
from sqlalchemy import Table


# ---------------------------------------------------------------------------
# Import contract
# ---------------------------------------------------------------------------

def test_tables_module_importable() -> None:
    import telegram_aggregator.storage.tables  # noqa: F401


def test_tables_exported_from_storage_package() -> None:
    from telegram_aggregator.storage import event_records, message_records
    assert event_records is not None
    assert message_records is not None


# ---------------------------------------------------------------------------
# Tables are registered in canonical metadata
# ---------------------------------------------------------------------------

def test_message_records_in_metadata() -> None:
    from telegram_aggregator.storage import metadata
    assert "message_records" in metadata.tables


def test_event_records_in_metadata() -> None:
    from telegram_aggregator.storage import metadata
    assert "event_records" in metadata.tables


def test_tables_are_sqlalchemy_table_instances() -> None:
    from telegram_aggregator.storage import event_records, message_records
    assert isinstance(message_records, Table)
    assert isinstance(event_records, Table)


# ---------------------------------------------------------------------------
# message_records columns
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("column_name", [
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
    "event_record_id",
    "status",
    "filter_reason",
    "target_message_id",
    "publish_attempts",
    "last_error",
    "received_at",
    "updated_at",
])
def test_message_records_has_column(column_name: str) -> None:
    from telegram_aggregator.storage import message_records
    assert column_name in message_records.c, (
        f"message_records missing column: {column_name!r}"
    )


# ---------------------------------------------------------------------------
# event_records columns
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("column_name", [
    "id",
    "target_channel",
    "event_type",
    "state",
    "started_at",
    "last_seen_at",
    "ended_at",
    "canonical_message_record_id",
    "published_target_message_id",
    "publish_status",
    "created_at",
    "updated_at",
])
def test_event_records_has_column(column_name: str) -> None:
    from telegram_aggregator.storage import event_records
    assert column_name in event_records.c, (
        f"event_records missing column: {column_name!r}"
    )


# ---------------------------------------------------------------------------
# Nullability
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("column_name", [
    "source_chat_id",
    "source_message_id",
    "has_media",
    "status",
    "publish_attempts",
    "received_at",
    "updated_at",
])
def test_message_records_required_columns_not_nullable(column_name: str) -> None:
    from telegram_aggregator.storage import message_records
    col = message_records.c[column_name]
    assert not col.nullable, f"message_records.{column_name} must be NOT NULL"


@pytest.mark.parametrize("column_name", [
    "source_title",
    "source_link",
    "raw_text",
    "normalized_text",
    "event_type",
    "event_signal",
    "candidate_signature",
    "event_record_id",
    "filter_reason",
    "target_message_id",
    "last_error",
])
def test_message_records_optional_columns_are_nullable(column_name: str) -> None:
    from telegram_aggregator.storage import message_records
    col = message_records.c[column_name]
    assert col.nullable, f"message_records.{column_name} must be nullable"


def test_event_records_ended_at_is_nullable() -> None:
    from telegram_aggregator.storage import event_records
    assert event_records.c["ended_at"].nullable


def test_event_records_required_columns_not_nullable() -> None:
    from telegram_aggregator.storage import event_records
    for col_name in ("target_channel", "event_type", "state", "started_at",
                     "last_seen_at", "publish_status", "created_at", "updated_at"):
        col = event_records.c[col_name]
        assert not col.nullable, f"event_records.{col_name} must be NOT NULL"


# ---------------------------------------------------------------------------
# Unique constraint on message_records
# ---------------------------------------------------------------------------

def test_message_records_has_unique_constraint_on_source_ids() -> None:
    from telegram_aggregator.storage import message_records

    unique_constraints = [
        c for c in message_records.constraints
        if hasattr(c, "columns")
        and set(col.name for col in c.columns) == {"source_chat_id", "source_message_id"}
    ]
    assert unique_constraints, (
        "message_records must have a unique constraint on (source_chat_id, source_message_id)"
    )


# ---------------------------------------------------------------------------
# Indexes on message_records
# ---------------------------------------------------------------------------

def test_message_records_has_status_index() -> None:
    from telegram_aggregator.storage import message_records

    index_columns = {
        frozenset(col.name for col in idx.columns)
        for idx in message_records.indexes
    }
    assert frozenset({"status"}) in index_columns, (
        "message_records must have an index on (status)"
    )


def test_message_records_has_composite_index() -> None:
    from telegram_aggregator.storage import message_records

    index_columns = {
        frozenset(col.name for col in idx.columns)
        for idx in message_records.indexes
    }
    assert frozenset({"event_type", "status", "received_at"}) in index_columns, (
        "message_records must have an index on (event_type, status, received_at)"
    )


# ---------------------------------------------------------------------------
# Foreign key: message_records -> event_records
# ---------------------------------------------------------------------------

def test_message_records_event_record_id_has_foreign_key() -> None:
    from telegram_aggregator.storage import message_records

    col = message_records.c["event_record_id"]
    assert col.foreign_keys, (
        "message_records.event_record_id must have a foreign key to event_records.id"
    )
    fk = next(iter(col.foreign_keys))
    assert fk.column.table.name == "event_records"
    assert fk.column.name == "id"


# ---------------------------------------------------------------------------
# Alembic revision file exists
# ---------------------------------------------------------------------------

def test_baseline_revision_file_exists() -> None:
    import pathlib
    versions_dir = pathlib.Path(__file__).parent.parent.parent / "alembic" / "versions"
    revision_files = list(versions_dir.glob("*.py"))
    assert revision_files, "alembic/versions/ must contain at least one revision file"


def test_baseline_revision_has_correct_down_revision() -> None:
    import pathlib
    import ast

    versions_dir = pathlib.Path(__file__).parent.parent.parent / "alembic" / "versions"
    revision_files = list(versions_dir.glob("*.py"))
    assert revision_files

    source = revision_files[0].read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "down_revision"
                for t in node.targets
            )
        ):
            assert isinstance(node.value, ast.Constant) and node.value.value is None, (
                "First revision must have down_revision = None"
            )
            return

        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "down_revision"
        ):
            assert (
                node.value is not None
                and isinstance(node.value, ast.Constant)
                and node.value.value is None
            ), "First revision must have down_revision = None"
            return

    pytest.fail("down_revision not found in revision file")
