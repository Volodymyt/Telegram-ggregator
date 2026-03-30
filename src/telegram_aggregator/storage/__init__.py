from __future__ import annotations

from telegram_aggregator.storage.engine import build_engine
from telegram_aggregator.storage.errors import (
    StorageConfigError,
    StorageMigrationError,
    StorageError,
)

from telegram_aggregator.storage.repository import (
    insert_message_idempotent,
    get_message_by_source,
    get_message_by_id,
    update_message_status,
    insert_event,
    get_event_by_id,
    update_event,
)

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
    "message_records",
    "event_records",
    "insert_message_idempotent",
    "get_message_by_source",
    "get_message_by_id",
    "update_message_status",
    "insert_event",
    "get_event_by_id",
    "update_event",
    "check_storage_readiness",
    "check_db_reachable",
    "check_migrations_current",
    "ReadinessResult",
    "ReadinessResult",
]
