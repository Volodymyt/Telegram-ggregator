from __future__ import annotations

from telegram_aggregator.storage.engine import build_engine
from telegram_aggregator.storage.errors import (
    StorageConfigError,
    StorageMigrationError,
    StorageError,
)
from telegram_aggregator.storage.facade import Repositories, Storage, build_storage
from telegram_aggregator.storage.repository import EventRepository, MessageRepository

from telegram_aggregator.storage.readiness import (
    check_storage_readiness,
    check_db_reachable,
    check_migrations_current,
    ReadinessResult,
)

from telegram_aggregator.storage.metadata import metadata
from telegram_aggregator.storage.tables import event_records, message_records

__all__ = [
    "build_engine",
    "metadata",
    "StorageError",
    "StorageConfigError",
    "StorageMigrationError",
    "Storage",
    "Repositories",
    "build_storage",
    "MessageRepository",
    "EventRepository",
    "message_records",
    "event_records",
    "check_storage_readiness",
    "check_db_reachable",
    "check_migrations_current",
    "ReadinessResult",
]
