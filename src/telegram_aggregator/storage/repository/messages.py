from __future__ import annotations

from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncConnection

from telegram_aggregator.storage.tables import message_records


async def insert_message_idempotent(
    conn: AsyncConnection,
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
        pg_insert(message_records)
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
        .returning(*message_records.c)
    )
    result = await conn.execute(stmt)
    row = result.mappings().first()

    if row is not None:
        return dict(row)

    # Row already existed — fetch and return it.
    existing = await get_message_by_source(
        conn,
        source_chat_id=source_chat_id,
        source_message_id=source_message_id,
    )
    assert existing is not None
    return existing


async def get_message_by_source(
    conn: AsyncConnection,
    *,
    source_chat_id: int,
    source_message_id: int,
) -> dict[str, Any] | None:
    stmt = sa.select(message_records).where(
        sa.and_(
            message_records.c.source_chat_id == source_chat_id,
            message_records.c.source_message_id == source_message_id,
        )
    )
    result = await conn.execute(stmt)
    row = result.mappings().first()
    return dict(row) if row is not None else None


async def get_message_by_id(
    conn: AsyncConnection,
    *,
    message_id: int,
) -> dict[str, Any] | None:
    stmt = sa.select(message_records).where(message_records.c.id == message_id)
    result = await conn.execute(stmt)
    row = result.mappings().first()
    return dict(row) if row is not None else None


async def update_message_status(
    conn: AsyncConnection,
    *,
    message_id: int,
    status: str,
    filter_reason: str | None = None,
    event_record_id: int | None = None,
    normalized_text: str | None = None,
    event_type: str | None = None,
    event_signal: str | None = None,
    candidate_signature: str | None = None,
) -> dict[str, Any] | None:
    values: dict[str, Any] = {"status": status}
    if filter_reason is not None:
        values["filter_reason"] = filter_reason
    if event_record_id is not None:
        values["event_record_id"] = event_record_id
    if normalized_text is not None:
        values["normalized_text"] = normalized_text
    if event_type is not None:
        values["event_type"] = event_type
    if event_signal is not None:
        values["event_signal"] = event_signal
    if candidate_signature is not None:
        values["candidate_signature"] = candidate_signature

    stmt = (
        sa.update(message_records)
        .where(message_records.c.id == message_id)
        .values(**values)
        .returning(*message_records.c)
    )
    result = await conn.execute(stmt)
    row = result.mappings().first()
    return dict(row) if row is not None else None
