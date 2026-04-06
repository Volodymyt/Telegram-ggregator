from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine

from telegram_aggregator.storage.engine import build_engine
from telegram_aggregator.storage.readiness import (
    ReadinessResult,
    check_storage_readiness,
)
from telegram_aggregator.storage.repository import EventRepository, MessageRepository


@dataclass(frozen=True)
class Repositories:
    messages: MessageRepository
    events: EventRepository


class Storage:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def check_readiness(self) -> ReadinessResult:
        return await check_storage_readiness(self._engine)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[Repositories]:
        async with self._engine.begin() as conn:
            yield Repositories(
                messages=MessageRepository(conn),
                events=EventRepository(conn),
            )

    async def close(self) -> None:
        await self._engine.dispose()


def build_storage(database_url: str) -> Storage:
    return Storage(build_engine(database_url))
