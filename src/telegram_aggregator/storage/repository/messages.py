from __future__ import annotations

from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncConnection

from telegram_aggregator.storage.tables import tg_message


class MessageRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self._conn = conn

    async def insert_message_idempotent(
        self,
        *,
        source_chat_id: int,
        source_message_id: int,
        source_title: str | None = None,
        source_link: str | None = None,
        raw_text: str | None = None,
        normalized_text: str | None = None,
        has_media: bool = False,
        event_type: str | None = None,
        event_signal: str | None = None,
        candidate_signature: str | None = None,
    ) -> dict[str, Any]:
        stmt = (
            pg_insert(tg_message)
            .values(
                source_chat_id=source_chat_id,
                source_message_id=source_message_id,
                source_title=source_title,
                source_link=source_link,
                raw_text=raw_text,
                normalized_text=normalized_text,
                has_media=has_media,
                event_type=event_type,
                event_signal=event_signal,
                candidate_signature=candidate_signature,
            )
            .on_conflict_do_nothing(
                index_elements=["source_chat_id", "source_message_id"],
            )
            .returning(*tg_message.c)
        )
        result = await self._conn.execute(stmt)
        row = result.mappings().first()

        if row is not None:
            return dict(row)

        existing = await self.get_message_by_source(
            source_chat_id=source_chat_id,
            source_message_id=source_message_id,
        )
        assert existing is not None
        return existing

    async def get_message_by_source(
        self,
        *,
        source_chat_id: int,
        source_message_id: int,
    ) -> dict[str, Any] | None:
        stmt = sa.select(tg_message).where(
            sa.and_(
                tg_message.c.source_chat_id == source_chat_id,
                tg_message.c.source_message_id == source_message_id,
            )
        )
        result = await self._conn.execute(stmt)
        row = result.mappings().first()
        return dict(row) if row is not None else None

    async def get_message_by_id(
        self,
        *,
        message_id: int,
    ) -> dict[str, Any] | None:
        stmt = sa.select(tg_message).where(tg_message.c.id == message_id)
        result = await self._conn.execute(stmt)
        row = result.mappings().first()
        return dict(row) if row is not None else None

    async def update_message_status(
        self,
        *,
        message_id: int,
        filter_reason: str | None = None,
        classification_status: str | None = None,
        aggregation_status: str | None = None,
        publish_status: str | None = None,
        event_id: int | None = None,
        normalized_text: str | None = None,
        event_type: str | None = None,
        event_signal: str | None = None,
        candidate_signature: str | None = None,
    ) -> dict[str, Any] | None:
        candidate_values: dict[str, Any] = {
            "classification_status": classification_status,
            "aggregation_status": aggregation_status,
            "publish_status": publish_status,
            "event_id": event_id,
            "normalized_text": normalized_text,
            "event_type": event_type,
            "event_signal": event_signal,
            "candidate_signature": candidate_signature,
            "filter_reason": filter_reason,
        }
        values = {
            key: value for key, value in candidate_values.items() if value is not None
        }

        if not values:
            return await self.get_message_by_id(message_id=message_id)

        stmt = (
            sa.update(tg_message)
            .where(tg_message.c.id == message_id)
            .values(**values)
            .returning(*tg_message.c)
        )
        result = await self._conn.execute(stmt)
        row = result.mappings().first()
        return dict(row) if row is not None else None
