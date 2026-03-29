from __future__ import annotations

from telegram_aggregator.storage.repository.events import (
    get_event_by_id,
    insert_event,
    update_event,
)
from telegram_aggregator.storage.repository.messages import (
    get_message_by_id,
    get_message_by_source,
    insert_message_idempotent,
    update_message_status,
)

__all__ = [
    "insert_message_idempotent",
    "get_message_by_source",
    "get_message_by_id",
    "update_message_status",
    "insert_event",
    "get_event_by_id",
    "update_event",
]
