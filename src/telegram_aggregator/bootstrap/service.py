"""Canonical service bootstrap entrypoint."""

from __future__ import annotations

import asyncio
import logging
import signal
from typing import TYPE_CHECKING

from telegram_aggregator.config.runtime import (
    RuntimeConfig,
    RuntimeConfigError,
    load_runtime_config,
)

if TYPE_CHECKING:
    from telegram_aggregator.reading.telegram_client import MessageInfo

logger = logging.getLogger(__name__)


class ServiceRuntime:
    """Temporary runtime wiring kept behind the canonical bootstrap surface."""

    def __init__(self, config: RuntimeConfig) -> None:
        from telegram_aggregator.processing.message_queue import MessageQueue
        from telegram_aggregator.reading.telegram_client import TelegramClient

        self._client = TelegramClient(config.telegram)
        self._message_queue = MessageQueue()

    async def run(self) -> None:
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

    async def on_new_message(self, message: MessageInfo) -> None:
        self._message_queue.push(message)


def run_service() -> None:
    """Route service startup through the canonical bootstrap boundary."""

    try:
        config = load_runtime_config()
    except RuntimeConfigError as exc:
        raise SystemExit(str(exc)) from None

    logging.basicConfig(
        level=config.logging.level,
        format=config.logging.format,
    )

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        asyncio.run(ServiceRuntime(config).run())
    except KeyboardInterrupt:
        pass