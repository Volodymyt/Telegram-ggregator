"""Unit coverage for the canonical service bootstrap entrypoint."""

from __future__ import annotations

import sqlite3
import asyncio
import json
import logging
from collections.abc import Callable
from pathlib import Path

import pytest

from telegram_aggregator.bootstrap.service import (
    ServiceRuntime,
    _configure_json_logging,
    run_service,
)
from telegram_aggregator.config import load_app_config
from telegram_aggregator.storage import ReadinessResult, StorageConfigError


class _FakeStorage:
    def __init__(
        self,
        events: list[object],
        *,
        readiness_results: list[ReadinessResult | Exception] | None = None,
    ) -> None:
        self._events = events
        self._readiness_results = readiness_results or [
            ReadinessResult(db_reachable=True, migrations_current=True)
        ]
        self._readiness_index = 0
        self.closed = False

    async def check_readiness(self) -> ReadinessResult:
        self._events.append("storage-check")
        result = self._readiness_results[
            min(self._readiness_index, len(self._readiness_results) - 1)
        ]
        self._readiness_index += 1

        if isinstance(result, Exception):
            raise result

        return result

    async def close(self) -> None:
        self.closed = True
        self._events.append("storage-close")


def _install_fake_storage(
    monkeypatch: pytest.MonkeyPatch,
    events: list[object],
    *,
    readiness_results: list[ReadinessResult | Exception] | None = None,
) -> _FakeStorage:
    storage = _FakeStorage(events, readiness_results=readiness_results)

    def _build_storage(database_url: str) -> _FakeStorage:
        events.append(("storage-build", database_url))
        return storage

    monkeypatch.setattr(
        "telegram_aggregator.bootstrap.service.build_storage",
        _build_storage,
    )
    return storage


async def _async_noop() -> None:
    return None


async def _wait_until(
    predicate: Callable[[], bool],
    *,
    timeout: float = 1,
) -> None:
    async def _poll() -> None:
        while not predicate():
            await asyncio.sleep(0)

    await asyncio.wait_for(_poll(), timeout=timeout)


class _ShutdownController:
    def __init__(self) -> None:
        self._event = asyncio.Event()

    async def wait(self) -> None:
        await self._event.wait()

    def trigger(self) -> None:
        self._event.set()


class _FakeQueue:
    def __init__(self, events: list[object]) -> None:
        self._events = events

    def run(self) -> None:
        self._events.append("queue-run")

    def push(self, message) -> None:
        self._events.append(("queue-push", message))

    def stop(self) -> None:
        self._events.append("queue-stop")


class _FakeClient:
    events: list[object] = []
    enter_event: asyncio.Event | None = None
    exit_event: asyncio.Event | None = None

    def __init__(self, config) -> None:
        self.events = type(self).events
        self.events.append(("client-init", config.dry_run, config.telegram.session_path))

    async def __aenter__(self):
        self.events.append("client-enter")
        if self.enter_event is not None:
            self.enter_event.set()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.events.append("client-exit")
        if self.exit_event is not None:
            self.exit_event.set()
        return False

    def subscribe_to_new_messages(self, callback) -> None:
        self.events.append("subscribe")

    async def get_user_channels(self) -> list[object]:
        self.events.append("get-user-channels")
        return []


def _install_fake_runtime_components(
    monkeypatch: pytest.MonkeyPatch,
    events: list[object],
) -> None:
    _FakeClient.events = events
    _FakeClient.enter_event = None
    _FakeClient.exit_event = None

    def _queue_factory() -> _FakeQueue:
        events.append("queue-init")
        return _FakeQueue(events)

    monkeypatch.setattr(
        "telegram_aggregator.processing.message_queue.MessageQueue",
        _queue_factory,
    )
    monkeypatch.setattr("telegram_aggregator.telegram.TelegramClient", _FakeClient)


def _disable_health_server(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _start(self) -> None:
        return None

    async def _stop(self) -> None:
        return None

    monkeypatch.setattr(ServiceRuntime, "_start_health_server", _start)
    monkeypatch.setattr(ServiceRuntime, "_stop_health_server", _stop)


@pytest.mark.asyncio
async def test_health_response_reports_not_ready_components(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(monkeypatch, events)

    config = load_app_config()
    runtime = ServiceRuntime(config)
    runtime._readiness.storage_ready = True
    runtime._readiness.telegram_ready = False
    runtime._readiness.workers_ready = False

    response = await runtime._handle_health(None)  # type: ignore[arg-type]
    payload = json.loads(response.text)

    assert response.status == 503
    assert payload == {
        "ok": False,
        "storage": True,
        "telegram": False,
        "workers": False,
    }


@pytest.mark.asyncio
async def test_health_response_reports_ready_runtime(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(monkeypatch, events)

    config = load_app_config()
    runtime = ServiceRuntime(config)
    runtime._readiness.storage_ready = True
    runtime._readiness.telegram_ready = True
    runtime._readiness.workers_ready = True

    response = await runtime._handle_health(None)  # type: ignore[arg-type]
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload == {
        "ok": True,
        "storage": True,
        "telegram": True,
        "workers": True,
    }


def test_configure_json_logging_emits_required_fields(capsys) -> None:
    _configure_json_logging(logging.INFO)
    logger = logging.getLogger("telegram_aggregator.tests")

    logger.info("hello")
    captured = capsys.readouterr()
    payload = json.loads(captured.err)

    assert payload["level"] == "INFO"
    assert payload["name"] == "telegram_aggregator.tests"
    assert payload["message"] == "hello"
    assert "asctime" in payload
    assert "lineno" in payload
    assert "exc_info" in payload


@pytest.mark.asyncio
async def test_storage_readiness_refresh_sets_ready_state(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=True, migrations_current=True),
            ReadinessResult(db_reachable=True, migrations_current=False),
            StorageConfigError("DB unreachable: connection refused"),
        ],
    )

    config = load_app_config()
    runtime = ServiceRuntime(config, storage_probe_interval=0.01)

    assert await runtime._refresh_storage_readiness() is True
    assert runtime._readiness.storage_ready is True

    assert await runtime._refresh_storage_readiness() is False
    assert runtime._readiness.storage_ready is False

    assert await runtime._refresh_storage_readiness() is False
    assert runtime._readiness.storage_ready is False


@pytest.mark.asyncio
async def test_storage_probe_failure_logs_without_formatter_error(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            StorageConfigError("DB unreachable: connection refused"),
        ],
    )

    config = load_app_config()
    runtime = ServiceRuntime(config)

    with caplog.at_level(logging.WARNING):
        assert await runtime._refresh_storage_readiness() is False

    assert "Storage readiness probe failed: DB unreachable: connection refused" in caplog.text


@pytest.mark.asyncio
async def test_runtime_waits_for_storage_before_telegram_bootstrap(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=False, migrations_current=False),
        ],
    )
    _install_fake_runtime_components(monkeypatch, events)

    shutdown = _ShutdownController()
    config = load_app_config()
    runtime = ServiceRuntime(
        config,
        storage_probe_interval=0.01,
        shutdown_waiter=shutdown.wait,
    )
    monkeypatch.setattr(runtime, "_start_health_server", _async_noop)
    monkeypatch.setattr(runtime, "_stop_health_server", _async_noop)

    task = asyncio.create_task(runtime.run())
    await asyncio.sleep(0.05)

    assert "client-enter" not in events
    assert "queue-run" not in events
    assert runtime._readiness.storage_ready is False
    assert runtime._readiness.telegram_ready is False
    assert runtime._readiness.workers_ready is False

    shutdown.trigger()
    await task
    assert "storage-close" in events


@pytest.mark.asyncio
async def test_shutdown_before_storage_ready_cleans_up_without_telegram(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=False, migrations_current=False),
        ],
    )
    _install_fake_runtime_components(monkeypatch, events)

    shutdown = _ShutdownController()
    config = load_app_config()
    runtime = ServiceRuntime(
        config,
        storage_probe_interval=0.01,
        shutdown_waiter=shutdown.wait,
    )
    monkeypatch.setattr(runtime, "_start_health_server", _async_noop)
    monkeypatch.setattr(runtime, "_stop_health_server", _async_noop)

    task = asyncio.create_task(runtime.run())
    await asyncio.sleep(0.02)
    shutdown.trigger()
    await task

    assert "client-enter" not in events
    assert "storage-close" in events
    assert runtime._readiness.storage_ready is False
    assert runtime._readiness.telegram_ready is False
    assert runtime._readiness.workers_ready is False


@pytest.mark.asyncio
async def test_storage_recovery_starts_telegram_and_workers(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=False, migrations_current=False),
            ReadinessResult(db_reachable=True, migrations_current=True),
        ],
    )
    _install_fake_runtime_components(monkeypatch, events)

    _FakeClient.enter_event = asyncio.Event()
    shutdown = _ShutdownController()
    config = load_app_config()
    runtime = ServiceRuntime(
        config,
        storage_probe_interval=0.01,
        shutdown_waiter=shutdown.wait,
    )
    monkeypatch.setattr(runtime, "_start_health_server", _async_noop)
    monkeypatch.setattr(runtime, "_stop_health_server", _async_noop)

    task = asyncio.create_task(runtime.run())
    try:
        await asyncio.wait_for(_FakeClient.enter_event.wait(), timeout=1)

        assert "client-enter" in events
        assert "subscribe" in events
        assert "queue-run" in events
        assert runtime._readiness.storage_ready is True
        assert runtime._readiness.telegram_ready is True
        assert runtime._readiness.workers_ready is True
    finally:
        shutdown.trigger()
        try:
            await task
        finally:
            _FakeClient.enter_event = None

    assert events.index("queue-run") < events.index("queue-stop")


@pytest.mark.asyncio
async def test_storage_degradation_keeps_telegram_connected(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=True, migrations_current=True),
            StorageConfigError("DB unreachable: connection refused"),
        ],
    )
    _install_fake_runtime_components(monkeypatch, events)

    _FakeClient.enter_event = asyncio.Event()
    shutdown = _ShutdownController()
    config = load_app_config()
    runtime = ServiceRuntime(
        config,
        storage_probe_interval=0.01,
        shutdown_waiter=shutdown.wait,
    )
    monkeypatch.setattr(runtime, "_start_health_server", _async_noop)
    monkeypatch.setattr(runtime, "_stop_health_server", _async_noop)

    task = asyncio.create_task(runtime.run())
    try:
        await asyncio.wait_for(_FakeClient.enter_event.wait(), timeout=1)
        await _wait_until(lambda: runtime._readiness.storage_ready is False)

        assert "client-enter" in events
        assert "client-exit" not in events
        assert runtime._readiness.storage_ready is False
        assert runtime._readiness.telegram_ready is True
        assert runtime._readiness.workers_ready is True
    finally:
        shutdown.trigger()
        try:
            await task
        finally:
            _FakeClient.enter_event = None

    assert "client-exit" in events
    assert events.index("queue-run") < events.index("queue-stop")


def test_run_service_exits_cleanly_on_missing_database_url(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(SystemExit, match="Missing required environment variable: DATABASE_URL"):
        run_service()


def test_run_service_exits_cleanly_on_invalid_log_level(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")

    with pytest.raises(SystemExit, match="Environment variable LOG_LEVEL must be one of:"):
        run_service()


def test_run_service_exits_cleanly_on_invalid_yaml_shape(
    set_service_env,
) -> None:
    config_file = set_service_env()
    config_file.write_text("sources: []\n", encoding="utf-8")

    with pytest.raises(
        SystemExit,
        match="Config section document root has invalid keys",
    ):
        run_service()


def test_run_service_exits_cleanly_on_invalid_identifier(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace(
            '  - "@channel1"\n',
            '  - "channel1"\n',
            1,
        ),
    )

    with pytest.raises(
        SystemExit,
        match="Config field sources\\[0\\] must be a Telegram source identifier",
    ):
        run_service()


def test_run_service_rejects_missing_session_file(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    set_service_env(dry_run="0")
    (tmp_path / "sessions").mkdir()
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=True, migrations_current=True),
        ],
    )
    _disable_health_server(monkeypatch)

    with pytest.raises(SystemExit, match="Telegram session file does not exist:"):
        run_service()


def test_run_service_surfaces_unauthorized_session(
    set_service_env,
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="0", create_session_file=True)
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=True, migrations_current=True),
        ],
    )
    _disable_health_server(monkeypatch)
    fake_client = fake_telethon_client_cls(authorized=False)

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    with pytest.raises(
        SystemExit,
        match="Telegram session is not authorized. Run `python -m telegram_aggregator.login` first.",
    ):
        run_service()


def test_run_service_surfaces_session_path_errors_from_post_connect_runtime(
    set_service_env,
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="0", create_session_file=True)
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=True, migrations_current=True),
        ],
    )
    _disable_health_server(monkeypatch)
    fake_client = fake_telethon_client_cls(
        dialog_iteration_exception=sqlite3.OperationalError("database disk image is malformed")
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    with pytest.raises(
        SystemExit,
        match="Telegram session path is not usable: .*database disk image is malformed",
    ):
        run_service()


def test_run_service_surfaces_unexpected_errors_as_clean_exit(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="0", create_session_file=True)
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=True, migrations_current=True),
        ],
    )
    _disable_health_server(monkeypatch)

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            OSError("network is unreachable")
        ),
    )

    with pytest.raises(
        SystemExit,
        match="Telegram session path is not usable: .*network is unreachable",
    ):
        run_service()


def test_run_service_keeps_storage_readiness_errors_nonfatal(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[StorageConfigError("DB unreachable: connection refused")],
    )
    _disable_health_server(monkeypatch)

    async def _wait_for_shutdown_signal(self) -> None:
        await asyncio.sleep(0.03)

    monkeypatch.setattr(
        ServiceRuntime,
        "_wait_for_shutdown_signal",
        _wait_for_shutdown_signal,
    )

    class _FakeClient:
        def __init__(self, config) -> None:
            events.append("client-init")

        async def __aenter__(self):
            raise AssertionError(
                "Telegram runtime must not start after storage readiness failure"
            )

        async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
            return False

    monkeypatch.setattr("telegram_aggregator.telegram.TelegramClient", _FakeClient)

    run_service()

    assert events == [
        ("storage-build", "postgresql+asyncpg://user:pass@localhost:5432/app"),
        "client-init",
        "storage-check",
        "storage-close",
    ]
