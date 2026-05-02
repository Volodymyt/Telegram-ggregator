"""Canonical service bootstrap entrypoint."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import signal
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiohttp import web
from pythonjsonlogger.json import JsonFormatter

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
_STORAGE_PROBE_INTERVAL = 10


@dataclass
class RuntimeReadiness:

    storage_ready: bool = False
    telegram_ready: bool = False
    workers_ready: bool = False

    def is_ready(self) -> bool:
        return self.storage_ready and self.telegram_ready and self.workers_ready


class ServiceRuntime:

    def __init__(
        self,
        config: AppConfig,
        *,
        storage_probe_interval: float = _STORAGE_PROBE_INTERVAL,
        shutdown_waiter: Callable[[], Awaitable[None]] | None = None,
        health_host: str = _HEALTH_HOST,
        health_port: int = _HEALTH_PORT,
    ) -> None:
        from telegram_aggregator.processing.message_queue import MessageQueue
        from telegram_aggregator.telegram import TelegramClient

        self._config = config
        self._storage = build_storage(config.database_url)
        self._client = TelegramClient(config)
        self._message_queue = MessageQueue()
        self._readiness = RuntimeReadiness()
        self._health_runner: web.AppRunner | None = None
        self._health_site: web.TCPSite | None = None
        self._tasks: list[asyncio.Task] = []
        self._storage_probe_interval = storage_probe_interval
        self._shutdown_waiter = shutdown_waiter or self._wait_for_shutdown_signal
        self._health_host = health_host
        self._health_port = health_port

    async def _wait_for_shutdown_signal(self) -> None:
        loop = asyncio.get_event_loop()
        done = asyncio.Event()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, done.set)
        try:
            await done.wait()
        finally:
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.remove_signal_handler(sig)

    async def _stop_all_tasks(self) -> None:
        tasks = list(self._tasks)
        self._tasks = []

        for task in tasks:
            task.cancel()

        if tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _refresh_storage_readiness(self) -> bool:
        try:
            result = await self._storage.check_readiness()
        except StorageError as exc:
            logger.warning("Storage readiness probe failed: %s", exc)
            self._readiness.storage_ready = False
            return False

        ready = result.db_reachable and result.migrations_current
        self._readiness.storage_ready = ready
        return ready

    async def _storage_probe_loop(self, storage_ready_event: asyncio.Event) -> None:
        while True:
            ready = await self._refresh_storage_readiness()
            if ready:
                storage_ready_event.set()
            else:
                storage_ready_event.clear()
            await asyncio.sleep(self._storage_probe_interval)

    async def _wait_for_storage_ready_or_shutdown(
        self,
        storage_ready_event: asyncio.Event,
        shutdown_task: asyncio.Task,
    ) -> bool:
        while not storage_ready_event.is_set():
            wait_task = asyncio.create_task(storage_ready_event.wait())
            done, pending = await asyncio.wait(
                {wait_task, shutdown_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            if wait_task in pending:
                wait_task.cancel()

            if shutdown_task in done:
                return False

        return True

    async def run(self) -> None:
        storage_ready_event = asyncio.Event()

        try:
            await self._start_health_server()

            probe_task = asyncio.create_task(
                self._storage_probe_loop(storage_ready_event)
            )
            self._tasks.append(probe_task)

            shutdown_task = asyncio.create_task(self._shutdown_waiter())
            self._tasks.append(shutdown_task)

            if not await self._wait_for_storage_ready_or_shutdown(
                storage_ready_event,
                shutdown_task,
            ):
                await shutdown_task
                return

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

                await shutdown_task

        finally:
            if self._readiness.workers_ready:
                self._message_queue.stop()
            self._readiness.workers_ready = False
            self._readiness.telegram_ready = False
            self._readiness.storage_ready = False
            await self._stop_all_tasks()
            await self._stop_health_server()
            await self._storage.close()

    async def on_new_message(self, message: MessageInfo) -> None:
        self._message_queue.push(message)

    async def _start_health_server(self) -> None:
        app = web.Application()
        app.router.add_get("/health", self._handle_health)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host=self._health_host, port=self._health_port)
        await site.start()

        self._health_runner = runner
        self._health_site = site
        logger.info(
            "Health endpoint listening on http://%s:%d/health",
            self._health_host,
            self._health_port,
        )

    async def _stop_health_server(self) -> None:
        if self._health_runner is not None:
            await self._health_runner.cleanup()
            self._health_runner = None
            self._health_site = None

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
    formatter = JsonFormatter(
        ["asctime", "levelname", "name", "lineno", "message", "exc_info"],
        rename_fields={"levelname": "level"},
    )
    handler.setFormatter(formatter)
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
