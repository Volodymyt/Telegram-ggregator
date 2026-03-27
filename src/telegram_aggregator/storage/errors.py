from __future__ import annotations


class StorageError(Exception):
    """Base class for all storage-layer errors."""


class StorageConfigError(StorageError):
    """Raised when storage cannot be initialised due to missing or invalid config."""


class StorageMigrationError(StorageError):
    """Raised when Alembic migration execution fails."""
