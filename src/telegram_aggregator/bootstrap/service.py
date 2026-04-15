"""Canonical service bootstrap entrypoint."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from aiohttp import web
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

_HEALTH_HOST = "127.0.0.1"
_HEALTH_PORT = 6456


class _JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


@dataclass
class RuntimeReadiness:

    storage_ready: bool = False
    telegram_ready: bool = False
    workers_ready: bool = False

    def is_ready(self) -> bool:
        return self.storage_ready and self.telegram_ready and self.workers_ready


class ServiceRuntime:

    def __init__(self, config: AppConfig) -> None:
        from telegram_aggregator.processing.message_queue import MessageQueue
        from telegram_aggregator.telegram import TelegramClient

        self._config = config
        self._storage = build_storage(config.database_url)
        self._client = TelegramClient(config)
        self._message_queue = MessageQueue()
        self._readiness = RuntimeReadiness()
        self._health_runner: web.AppRunner | None = None

    async def run(self) -> None:
        try:
            await self._start_health_server()
            await self._storage.check_readiness()
            self._readiness.storage_ready = True

            async with self._client as client:
                self._readiness.telegram_ready = True
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

                self._readiness.workers_ready = True
                self._message_queue.run()
                await client.run_until_disconnected()
        finally:
            self._readiness.workers_ready = False
            self._readiness.telegram_ready = False
            self._readiness.storage_ready = False
            await self._stop_health_server()
            await self._storage.close()

    async def on_new_message(self, message: MessageInfo) -> None:
        self._message_queue.push(message)

    async def _start_health_server(self) -> None:
        app = web.Application()
        app.router.add_get("/health", self._handle_health)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host=_HEALTH_HOST, port=_HEALTH_PORT)
        await site.start()

        self._health_runner = runner
        logger.info(
            "Health endpoint listening on http://%s:%d/health",
            _HEALTH_HOST,
            _HEALTH_PORT,
        )

    async def _stop_health_server(self) -> None:
        if self._health_runner is not None:
            await self._health_runner.cleanup()
            self._health_runner = None

    async def _handle_health(self, _request: web.Request) -> web.Response:
        ready = self._readiness.is_ready()
        payload = {
            "ok": ready,
            "storage": self._readiness.storage_ready,
            "telegram": self._readiness.telegram_ready,
            "workers": self._readiness.workers_ready,
        }
        status = 200 if ready else 503
        return web.json_response(payload, status=status)


def _configure_json_logging(level: int) -> None:
    root = logging.getLogger()
    root.setLevel(level)

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())
    root.addHandler(handler)


def run_service() -> None:
    """Route service startup through the canonical bootstrap boundary."""
    try:
        config = load_app_config()
    except AppConfigError as exc:
        raise SystemExit(str(exc)) from None

    _configure_json_logging(config.log_level)

    try:
        runtime = ServiceRuntime(config)
        asyncio.run(runtime.run())
    except (SessionAuthorizationError, SessionPathError, StorageError) as exc:
        raise SystemExit(str(exc)) from None
    except Exception as exc:
        logger.error("Service failed: %s", exc)
        raise SystemExit(1) from None
