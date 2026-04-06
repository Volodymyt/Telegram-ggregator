from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import sqlalchemy as sa
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.ext.asyncio import AsyncEngine

from telegram_aggregator.storage.errors import (
    StorageConfigError,
    StorageMigrationError,
)


@dataclass(frozen=True)
class ReadinessResult:
    db_reachable: bool
    migrations_current: bool


def _get_alembic_script_location() -> str:
    script_location = Path.cwd() / "alembic"

    if not script_location.is_dir():
        raise StorageMigrationError(
            "Cannot locate Alembic migration scripts in the current working "
            f"directory: expected {script_location}. "
            "Start the service from the repository root or a directory that "
            "contains the alembic/ folder."
        )

    return str(script_location)


async def check_db_reachable(engine: AsyncEngine) -> None:
    try:
        async with engine.connect() as conn:
            await conn.execute(sa.text("SELECT 1"))
    except Exception as exc:
        raise StorageConfigError(f"DB unreachable: {exc}") from exc


async def check_migrations_current(engine: AsyncEngine) -> None:
    alembic_cfg = Config()
    alembic_cfg.set_main_option(
        "script_location",
        _get_alembic_script_location(),
    )

    try:
        script = ScriptDirectory.from_config(alembic_cfg)
        head_revisions = set(script.get_heads())
    except Exception as exc:
        raise StorageMigrationError(
            f"Cannot read Alembic migration scripts: {exc}."
        ) from exc

    try:
        async with engine.connect() as conn:
            context = await conn.run_sync(
                lambda sync_conn: MigrationContext.configure(sync_conn)
            )
            current_revisions = set(context.get_current_heads())
    except Exception as exc:
        raise StorageMigrationError(f"Cannot read migration state: {exc}") from exc

    if current_revisions != head_revisions:
        raise StorageMigrationError(
            f"Schema stale: current={current_revisions or '(none)'}, "
            f"expected={head_revisions}. Run: alembic upgrade head"
        )


async def check_storage_readiness(engine: AsyncEngine) -> ReadinessResult:
    await check_db_reachable(engine)
    await check_migrations_current(engine)
    return ReadinessResult(db_reachable=True, migrations_current=True)
