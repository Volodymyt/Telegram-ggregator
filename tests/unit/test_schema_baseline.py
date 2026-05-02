from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
from sqlalchemy import String, Table, Text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERSIONS_DIR = PROJECT_ROOT / "alembic" / "versions"

EXPECTED_STATUS_COLUMNS = (
    ("event", "publish_status"),
    ("tg_message", "classification_status"),
    ("tg_message", "aggregation_status"),
    ("tg_message", "publish_status"),
)


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


def _load_revision_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _assert_status_column_migration_calls(
    calls: list[tuple[str, str, dict[str, object]]],
    *,
    existing_type: type[object],
    target_type: type[object],
    target_length: int | None,
) -> None:
    assert [(table_name, column_name) for table_name, column_name, _ in calls] == list(
        EXPECTED_STATUS_COLUMNS
    )

    for _, _, kwargs in calls:
        assert isinstance(kwargs["existing_type"], existing_type)
        assert isinstance(kwargs["type_"], target_type)
        assert kwargs["existing_nullable"] is False
        assert getattr(kwargs["type_"], "length", None) == target_length


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


def test_status_columns_preserve_server_defaults() -> None:
    from telegram_aggregator.storage import event, tg_message

    status_defaults = (
        (event.c.publish_status, "pending"),
        (tg_message.c.classification_status, "pending"),
        (tg_message.c.aggregation_status, "new"),
        (tg_message.c.publish_status, "new"),
    )

    for column, expected_default in status_defaults:
        assert column.server_default is not None
        assert column.server_default.arg == expected_default


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


def test_status_column_type_revision_alters_all_status_columns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_revision_module(VERSIONS_DIR / "0002_status_columns_varchar_32.py")
    assert module.STATUS_COLUMNS == EXPECTED_STATUS_COLUMNS

    calls: list[tuple[str, str, dict[str, object]]] = []

    def alter_column(table_name: str, column_name: str, **kwargs: object) -> None:
        calls.append((table_name, column_name, kwargs))

    monkeypatch.setattr(module.op, "alter_column", alter_column)

    module.upgrade()
    upgrade_calls = calls.copy()

    calls.clear()
    module.downgrade()
    downgrade_calls = calls.copy()

    _assert_status_column_migration_calls(
        upgrade_calls,
        existing_type=Text,
        target_type=String,
        target_length=32,
    )
    _assert_status_column_migration_calls(
        downgrade_calls,
        existing_type=String,
        target_type=Text,
        target_length=None,
    )
