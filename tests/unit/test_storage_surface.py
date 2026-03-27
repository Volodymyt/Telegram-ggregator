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
