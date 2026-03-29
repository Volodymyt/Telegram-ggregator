from __future__ import annotations

from datetime import datetime
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from telegram_aggregator.storage.tables import event_records


async def insert_event(
    conn: AsyncConnection,
    *,
    target_channel: str,
    event_type: str,
    state: str = "open",
    canonical_message_record_id: int | None = None,
) -> dict[str, Any]:
    stmt = (
        sa.insert(event_records)
        .values(
            target_channel=target_channel,
            event_type=event_type,
            state=state,
            canonical_message_record_id=canonical_message_record_id,
        )
        .returning(*event_records.c)
    )
    result = await conn.execute(stmt)
    row = result.mappings().first()
    assert row is not None
    return dict(row)


async def get_event_by_id(
    conn: AsyncConnection,
    *,
    event_id: int,
) -> dict[str, Any] | None:
    stmt = sa.select(event_records).where(event_records.c.id == event_id)
    result = await conn.execute(stmt)
    row = result.mappings().first()
    return dict(row) if row is not None else None


async def update_event(
    conn: AsyncConnection,
    *,
    event_id: int,
    state: str | None = None,
    last_seen_at: datetime | None = None,
    ended_at: datetime | None = None,
    canonical_message_record_id: int | None = None,
    published_target_message_id: int | None = None,
    publish_status: str | None = None,
) -> dict[str, Any] | None:
    values: dict[str, Any] = {}
    if state is not None:
        values["state"] = state
    if last_seen_at is not None:
        values["last_seen_at"] = last_seen_at
    if ended_at is not None:
        values["ended_at"] = ended_at
    if canonical_message_record_id is not None:
        values["canonical_message_record_id"] = canonical_message_record_id
    if published_target_message_id is not None:
        values["published_target_message_id"] = published_target_message_id
    if publish_status is not None:
        values["publish_status"] = publish_status

    if not values:
        return await get_event_by_id(conn, event_id=event_id)

    stmt = (
        sa.update(event_records)
        .where(event_records.c.id == event_id)
        .values(**values)
        .returning(*event_records.c)
    )
    result = await conn.execute(stmt)
    row = result.mappings().first()
    return dict(row) if row is not None else None
