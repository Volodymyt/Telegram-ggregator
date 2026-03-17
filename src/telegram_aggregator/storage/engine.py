from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from telegram_aggregator.storage.errors import StorageConfigError


def build_engine(database_url: str) -> AsyncEngine:
    if not database_url or not database_url.strip():
        raise StorageConfigError(
            "DATABASE_URL must be a non-empty string. "
            "Ensure it is present in the environment before initialising storage."
        )

    return create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )