"""Unit tests for the canonical storage surface (task 0013).

These tests validate the storage package contract without a running database:
  - public API is importable from the canonical surface
  - build_engine rejects empty / missing DATABASE_URL
  - build_engine accepts a valid DSN and returns an AsyncEngine
  - metadata is a MetaData instance with the expected naming convention
  - error hierarchy is correct
  - alembic env.py resolves target_metadata to the canonical metadata object
"""

from __future__ import annotations

import importlib
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine


# ---------------------------------------------------------------------------
# Import contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_name",
    [
        "telegram_aggregator.storage",
        "telegram_aggregator.storage.engine",
        "telegram_aggregator.storage.metadata",
        "telegram_aggregator.storage.errors",
        "telegram_aggregator.storage.facade",
        "telegram_aggregator.storage.repository",
    ],
)
def test_storage_modules_importable(module_name: str) -> None:
    """All canonical storage sub-modules must be importable."""
    module = importlib.import_module(module_name)
    assert module is not None


def test_storage_public_api() -> None:
    """The storage package must export its full public API from __init__."""
    import telegram_aggregator.storage as storage

    assert hasattr(storage, "build_engine"), "build_engine missing from public API"
    assert hasattr(storage, "build_storage"), "build_storage missing from public API"
    assert hasattr(storage, "Storage"), "Storage missing from public API"
    assert hasattr(storage, "Repositories"), "Repositories missing from public API"
    assert hasattr(storage.Storage, "check_readiness"), "Storage.check_readiness missing from public API"
    assert hasattr(storage, "MessageRepository"), "MessageRepository missing from public API"
    assert hasattr(storage, "EventRepository"), "EventRepository missing from public API"
    assert hasattr(storage, "metadata"), "metadata missing from public API"
    assert hasattr(storage, "StorageError"), "StorageError missing from public API"
    assert hasattr(storage, "StorageConfigError"), "StorageConfigError missing from public API"
    assert hasattr(storage, "StorageMigrationError"), "StorageMigrationError missing from public API"


# ---------------------------------------------------------------------------
# metadata object
# ---------------------------------------------------------------------------


def test_metadata_is_sqlalchemy_metadata() -> None:
    """storage.metadata must be a SQLAlchemy MetaData instance."""
    from telegram_aggregator.storage import metadata

    assert isinstance(metadata, MetaData)


def test_metadata_has_naming_convention() -> None:
    """metadata must carry a naming convention so Alembic can name constraints."""
    from telegram_aggregator.storage import metadata

    nc = metadata.naming_convention
    assert nc, "naming_convention must not be empty"

    # These four keys are the minimum required for safe Alembic autogenerate.
    for key in ("ix", "uq", "fk", "pk"):
        assert key in nc, f"naming_convention missing key: {key!r}"


def test_metadata_is_singleton() -> None:
    """Importing metadata twice must return the identical object."""
    from telegram_aggregator.storage import metadata as m1
    from telegram_aggregator.storage.metadata import metadata as m2

    assert m1 is m2, "metadata must be a module-level singleton, not re-created on import"


# ---------------------------------------------------------------------------
# build_engine — error cases
# ---------------------------------------------------------------------------


def test_build_engine_raises_on_empty_url() -> None:
    """build_engine must raise StorageConfigError for an empty string."""
    from telegram_aggregator.storage import StorageConfigError, build_engine

    with pytest.raises(StorageConfigError):
        build_engine("")


def test_build_engine_raises_on_whitespace_url() -> None:
    """build_engine must raise StorageConfigError for a whitespace-only string."""
    from telegram_aggregator.storage import StorageConfigError, build_engine

    with pytest.raises(StorageConfigError):
        build_engine("   ")


# ---------------------------------------------------------------------------
# build_engine — happy path (no real DB needed)
# ---------------------------------------------------------------------------


def test_build_engine_returns_async_engine() -> None:
    """build_engine must return an AsyncEngine for a valid DSN."""
    from telegram_aggregator.storage import build_engine

    engine = build_engine("postgresql+asyncpg://user:pass@localhost/testdb")

    assert isinstance(engine, AsyncEngine)


def test_build_engine_different_calls_return_independent_engines() -> None:
    """Each call to build_engine must produce an independent engine instance."""
    from telegram_aggregator.storage import build_engine

    url = "postgresql+asyncpg://user:pass@localhost/testdb"
    e1 = build_engine(url)
    e2 = build_engine(url)

    assert e1 is not e2


def test_build_storage_wraps_engine() -> None:
    """build_storage must return the higher-level storage facade."""
    from telegram_aggregator.storage import Storage, build_storage

    storage = build_storage("postgresql+asyncpg://user:pass@localhost/testdb")

    assert isinstance(storage, Storage)


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------


def test_storage_config_error_is_storage_error() -> None:
    """StorageConfigError must be a subclass of StorageError."""
    from telegram_aggregator.storage import StorageConfigError, StorageError

    assert issubclass(StorageConfigError, StorageError)


def test_storage_migration_error_is_storage_error() -> None:
    """StorageMigrationError must be a subclass of StorageError."""
    from telegram_aggregator.storage import StorageMigrationError, StorageError

    assert issubclass(StorageMigrationError, StorageError)


def test_storage_error_is_exception() -> None:
    """StorageError must be a subclass of the built-in Exception."""
    from telegram_aggregator.storage import StorageError

    assert issubclass(StorageError, Exception)


# ---------------------------------------------------------------------------
# Repository contract
# ---------------------------------------------------------------------------


def test_message_repository_exposes_crud_methods() -> None:
    from telegram_aggregator.storage import MessageRepository

    for method_name in (
        "insert_message_idempotent",
        "get_message_by_source",
        "get_message_by_id",
        "update_message_status",
    ):
        assert hasattr(MessageRepository, method_name), (
            f"MessageRepository missing method: {method_name}"
        )


def test_event_repository_exposes_crud_methods() -> None:
    from telegram_aggregator.storage import EventRepository

    for method_name in (
        "insert_event",
        "get_event_by_id",
        "update_event",
    ):
        assert hasattr(EventRepository, method_name), (
            f"EventRepository missing method: {method_name}"
        )


# ---------------------------------------------------------------------------
# Storage facade
# ---------------------------------------------------------------------------


class _FakeBegin:
    def __init__(self, conn: object) -> None:
        self._conn = conn

    async def __aenter__(self) -> object:
        return self._conn

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeEngine:
    def __init__(self) -> None:
        self.conn = object()
        self.begin_calls = 0
        self.dispose_calls = 0

    def begin(self) -> _FakeBegin:
        self.begin_calls += 1
        return _FakeBegin(self.conn)

    async def dispose(self) -> None:
        self.dispose_calls += 1


@pytest.mark.asyncio
async def test_storage_transaction_yields_repositories() -> None:
    from telegram_aggregator.storage import EventRepository, MessageRepository, Storage

    engine = _FakeEngine()
    storage = Storage(engine=engine)  # type: ignore[arg-type]

    async with storage.transaction() as repos:
        assert isinstance(repos.messages, MessageRepository)
        assert isinstance(repos.events, EventRepository)
        assert repos.messages._conn is engine.conn
        assert repos.events._conn is engine.conn

    assert engine.begin_calls == 1


@pytest.mark.asyncio
async def test_storage_close_disposes_engine() -> None:
    from telegram_aggregator.storage import Storage

    engine = _FakeEngine()
    storage = Storage(engine=engine)  # type: ignore[arg-type]

    await storage.close()

    assert engine.dispose_calls == 1


@pytest.mark.asyncio
async def test_storage_check_readiness_uses_internal_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from telegram_aggregator.storage import ReadinessResult, Storage

    engine = object()
    storage = Storage(engine=engine)  # type: ignore[arg-type]
    expected = ReadinessResult(db_reachable=True, migrations_current=True)

    async def fake_check_storage_readiness(actual_engine: object) -> ReadinessResult:
        assert actual_engine is engine
        return expected

    monkeypatch.setattr(
        "telegram_aggregator.storage.facade.check_storage_readiness",
        fake_check_storage_readiness,
    )

    result = await storage.check_readiness()

    assert result == expected


class _FakeMappingsResult:
    def __init__(self, row: dict[str, object] | None) -> None:
        self._row = row

    def first(self) -> dict[str, object] | None:
        return self._row


class _FakeExecuteResult:
    def __init__(self, row: dict[str, object] | None) -> None:
        self._row = row

    def mappings(self) -> _FakeMappingsResult:
        return _FakeMappingsResult(self._row)


class _RecordingConnection:
    def __init__(self, row: dict[str, object] | None = None) -> None:
        self._row = row
        self.executed: list[object] = []

    async def execute(self, stmt: object) -> _FakeExecuteResult:
        self.executed.append(stmt)
        return _FakeExecuteResult(self._row)


@pytest.mark.asyncio
async def test_event_repository_update_event_returns_current_row_for_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from telegram_aggregator.storage import EventRepository

    conn = _RecordingConnection()
    repo = EventRepository(conn=conn)  # type: ignore[arg-type]
    existing_row = {"id": 7, "state": "open"}

    async def fake_get_event_by_id(*, event_id: int) -> dict[str, object]:
        assert event_id == 7
        return existing_row

    monkeypatch.setattr(repo, "get_event_by_id", fake_get_event_by_id)

    result = await repo.update_event(event_id=7)

    assert result == existing_row
    assert conn.executed == []


@pytest.mark.asyncio
async def test_event_repository_update_event_updates_only_provided_field() -> None:
    from telegram_aggregator.storage import EventRepository

    conn = _RecordingConnection(row={"id": 7, "state": "closed"})
    repo = EventRepository(conn=conn)  # type: ignore[arg-type]

    result = await repo.update_event(event_id=7, state="closed")

    assert result == {"id": 7, "state": "closed"}
    assert len(conn.executed) == 1

    stmt = conn.executed[0]
    params = stmt.compile().params

    assert params["id_1"] == 7
    assert params["state"] == "closed"
    assert set(params) == {"id_1", "state"}


@pytest.mark.asyncio
async def test_event_repository_update_event_filters_out_none_values() -> None:
    from telegram_aggregator.storage import EventRepository

    last_seen_at = datetime(2026, 4, 6, tzinfo=timezone.utc)
    conn = _RecordingConnection(
        row={
            "id": 7,
            "state": "closed",
            "last_seen_at": last_seen_at,
            "publish_status": "failed",
        }
    )
    repo = EventRepository(conn=conn)  # type: ignore[arg-type]

    result = await repo.update_event(
        event_id=7,
        state="closed",
        last_seen_at=last_seen_at,
        ended_at=None,
        publish_status="failed",
    )

    assert result == {
        "id": 7,
        "state": "closed",
        "last_seen_at": last_seen_at,
        "publish_status": "failed",
    }
    assert len(conn.executed) == 1

    stmt = conn.executed[0]
    params = stmt.compile().params

    assert params["id_1"] == 7
    assert params["state"] == "closed"
    assert params["last_seen_at"] == last_seen_at
    assert params["publish_status"] == "failed"
    assert "ended_at" not in params
    assert set(params) == {"id_1", "state", "last_seen_at", "publish_status"}


@pytest.mark.asyncio
async def test_message_repository_update_message_status_filters_out_none_values() -> None:
    from telegram_aggregator.storage import MessageRepository

    conn = _RecordingConnection(
        row={
            "id": 11,
            "status": "candidate",
            "event_record_id": 7,
            "event_type": "ballistic",
        }
    )
    repo = MessageRepository(conn=conn)  # type: ignore[arg-type]

    result = await repo.update_message_status(
        message_id=11,
        status="candidate",
        filter_reason=None,
        event_record_id=7,
        normalized_text=None,
        event_type="ballistic",
        event_signal=None,
        candidate_signature=None,
    )

    assert result == {
        "id": 11,
        "status": "candidate",
        "event_record_id": 7,
        "event_type": "ballistic",
    }
    assert len(conn.executed) == 1

    stmt = conn.executed[0]
    params = stmt.compile().params

    assert params["id_1"] == 11
    assert params["status"] == "candidate"
    assert params["event_record_id"] == 7
    assert params["event_type"] == "ballistic"
    assert "filter_reason" not in params
    assert "normalized_text" not in params
    assert "event_signal" not in params
    assert "candidate_signature" not in params
    assert set(params) == {"id_1", "status", "event_record_id", "event_type"}


# ---------------------------------------------------------------------------
# Alembic env.py — target_metadata points to canonical metadata
# ---------------------------------------------------------------------------


def test_alembic_env_target_metadata_is_canonical_metadata() -> None:
    """alembic/env.py must wire target_metadata to the canonical storage metadata."""
    import pathlib
    import ast

    project_root = pathlib.Path(__file__).parent.parent.parent
    env_file = project_root / "alembic" / "env.py"

    assert env_file.exists(), "alembic/env.py must exist"

    source = env_file.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Look for: target_metadata = metadata
    assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
    ]

    target_metadata_assigned = any(
        any(
            isinstance(t, ast.Name) and t.id == "target_metadata"
            for t in node.targets
        )
        for node in assignments
    )

    assert target_metadata_assigned, (
        "alembic/env.py must assign target_metadata at module level"
    )

    # Confirm it imports from the canonical storage module
    imports = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    ]

    imports_from_storage_metadata = any(
        node.module == "telegram_aggregator.storage.metadata"
        for node in imports
    )

    assert imports_from_storage_metadata, (
        "alembic/env.py must import from telegram_aggregator.storage.metadata"
    )


def test_readiness_resolves_existing_alembic_directory() -> None:
    import telegram_aggregator.storage.readiness as readiness

    script_location = Path(readiness._get_alembic_script_location())

    assert script_location.exists(), "readiness must point to an existing alembic directory"
    assert script_location.name == "alembic"


@pytest.mark.asyncio
async def test_check_storage_readiness_returns_success_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from telegram_aggregator.storage import ReadinessResult, check_storage_readiness

    engine = object()
    calls: list[str] = []

    async def fake_check_db_reachable(actual_engine: object) -> None:
        assert actual_engine is engine
        calls.append("db")

    async def fake_check_migrations_current(actual_engine: object) -> None:
        assert actual_engine is engine
        calls.append("migrations")

    monkeypatch.setattr(
        "telegram_aggregator.storage.readiness.check_db_reachable",
        fake_check_db_reachable,
    )
    monkeypatch.setattr(
        "telegram_aggregator.storage.readiness.check_migrations_current",
        fake_check_migrations_current,
    )

    result = await check_storage_readiness(engine)  # type: ignore[arg-type]

    assert result == ReadinessResult(db_reachable=True, migrations_current=True)
    assert calls == ["db", "migrations"]


@pytest.mark.asyncio
async def test_check_storage_readiness_propagates_storage_config_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from telegram_aggregator.storage import (
        StorageConfigError,
        check_storage_readiness,
    )

    async def fake_check_db_reachable(_: object) -> None:
        raise StorageConfigError("DB unreachable")

    async def fake_check_migrations_current(_: object) -> None:
        raise AssertionError("migration check must not run after DB failure")

    monkeypatch.setattr(
        "telegram_aggregator.storage.readiness.check_db_reachable",
        fake_check_db_reachable,
    )
    monkeypatch.setattr(
        "telegram_aggregator.storage.readiness.check_migrations_current",
        fake_check_migrations_current,
    )

    with pytest.raises(StorageConfigError, match="DB unreachable"):
        await check_storage_readiness(object())  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_check_storage_readiness_propagates_storage_migration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from telegram_aggregator.storage import (
        StorageMigrationError,
        check_storage_readiness,
    )

    async def fake_check_db_reachable(_: object) -> None:
        return None

    async def fake_check_migrations_current(_: object) -> None:
        raise StorageMigrationError("Schema stale")

    monkeypatch.setattr(
        "telegram_aggregator.storage.readiness.check_db_reachable",
        fake_check_db_reachable,
    )
    monkeypatch.setattr(
        "telegram_aggregator.storage.readiness.check_migrations_current",
        fake_check_migrations_current,
    )

    with pytest.raises(StorageMigrationError, match="Schema stale"):
        await check_storage_readiness(object())  # type: ignore[arg-type]
