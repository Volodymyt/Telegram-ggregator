"""Canonical service bootstrap entrypoint."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from telegram_aggregator.config import (
    AppConfig,
    AppConfigError,
    load_app_config,
)
from telegram_aggregator.storage import StorageError, build_storage
from telegram_aggregator.telegram import (
    SessionAuthorizationError,
    SessionPathError,
)

if TYPE_CHECKING:
    from telegram_aggregator.telegram import MessageInfo

logger = logging.getLogger(__name__)
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class ServiceRuntime:
    """Current runtime wiring behind the canonical bootstrap surface."""

    def __init__(self, config: AppConfig) -> None:
        from telegram_aggregator.processing.message_queue import MessageQueue
        from telegram_aggregator.telegram import TelegramClient

        self._storage = build_storage(config.database_url)
        self._client = TelegramClient(config)
        self._message_queue = MessageQueue()

    async def run(self) -> None:
        try:
            await self._storage.check_readiness()

            async with self._client as client:
                client.subscribe_to_new_messages(self.on_new_message)

                logger.info("Listening for new messages")
                logger.info("Load channels...")
                channels = await client.get_user_channels()

                for channel in channels:
                    logger.info("  channel • [%s] %s", channel.tg_id, channel.title)

                logger.info("Load history...")

                if channels:
                    messages = await client.fetch_channel_history(
                        channels[0].tg_id,
                        limit=50,
                    )

                    for message in messages:
                        self._message_queue.push(message)

                self._message_queue.run()
                await client.run_until_disconnected()
        finally:
            await self._storage.close()

    async def on_new_message(self, message: MessageInfo) -> None:
        self._message_queue.push(message)


def run_service() -> None:
    """Route service startup through the canonical bootstrap boundary."""
    try:
        config = load_app_config()
    except AppConfigError as exc:
        raise SystemExit(str(exc)) from None

    logging.basicConfig(
        level=config.log_level,
        format=_LOG_FORMAT,
    )

    try:
        runtime = ServiceRuntime(config)
        asyncio.run(runtime.run())
    except (SessionAuthorizationError, SessionPathError, StorageError) as exc:
        raise SystemExit(str(exc)) from None
    except Exception as exc:
        logger.error("Service failed: %s", exc)
        raise SystemExit(1) from None
