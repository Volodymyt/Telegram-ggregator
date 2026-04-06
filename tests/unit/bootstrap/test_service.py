"""Unit coverage for the canonical service bootstrap entrypoint."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from telegram_aggregator.bootstrap.service import run_service
from telegram_aggregator.storage import StorageConfigError


class _FakeStorage:
    def __init__(
        self,
        events: list[object],
        *,
        check_exception: Exception | None = None,
    ) -> None:
        self._events = events
        self._check_exception = check_exception

    async def check_readiness(self):
        self._events.append("storage-check")

        if self._check_exception is not None:
            raise self._check_exception

        return object()

    async def close(self) -> None:
        self._events.append("storage-close")


def _install_fake_storage(
    monkeypatch: pytest.MonkeyPatch,
    events: list[object],
    *,
    check_exception: Exception | None = None,
) -> _FakeStorage:
    storage = _FakeStorage(events, check_exception=check_exception)

    def _build_storage(database_url: str) -> _FakeStorage:
        events.append(("storage-build", database_url))
        return storage

    monkeypatch.setattr(
        "telegram_aggregator.bootstrap.service.build_storage",
        _build_storage,
    )
    return storage


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


def test_run_service_dry_run_skips_telegram_runtime(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(monkeypatch, events)

    class _FakeQueue:
        def run(self) -> None:
            events.append("queue-run")

        def push(self, message) -> None:
            events.append(("queue-push", message))

    class _FakeClient:
        def __init__(self, config) -> None:
            events.append(
                ("client-init", config.dry_run, config.telegram.session_path)
            )

        async def __aenter__(self):
            events.append("client-enter")
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
            events.append("client-exit")
            return False

        def subscribe_to_new_messages(self, callback) -> None:
            events.append("subscribe")

        async def get_user_channels(self) -> list[object]:
            events.append("get-user-channels")
            return []

        async def run_until_disconnected(self) -> None:
            events.append("run-until-disconnected")
            return None

    monkeypatch.setattr("telegram_aggregator.processing.message_queue.MessageQueue", _FakeQueue)
    monkeypatch.setattr("telegram_aggregator.telegram.TelegramClient", _FakeClient)

    run_service()

    assert events == [
        ("storage-build", "postgresql+asyncpg://user:pass@localhost:5432/app"),
        ("client-init", True, (tmp_path / "sessions/default.session").resolve()),
        "storage-check",
        "client-enter",
        "subscribe",
        "get-user-channels",
        "queue-run",
        "run-until-disconnected",
        "client-exit",
        "storage-close",
    ]


def test_run_service_rejects_missing_session_file(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    set_service_env(dry_run="0")
    (tmp_path / "sessions").mkdir()
    _install_fake_storage(monkeypatch, [])

    with pytest.raises(SystemExit, match="Telegram session file does not exist:"):
        run_service()


def test_run_service_uses_telegram_runtime_when_not_dry_run(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="0", create_session_file=True)
    captured: dict[str, object] = {}
    storage_events: list[object] = []
    _install_fake_storage(monkeypatch, storage_events)

    class _FakeQueue:
        def run(self) -> None:
            captured["queue_run"] = True

        def push(self, message) -> None:
            captured.setdefault("pushed", []).append(message)

    class _FakeClient:
        def __init__(self, config) -> None:
            captured["dry_run"] = config.dry_run
            captured["session_path"] = config.telegram.session_path

        async def __aenter__(self):
            captured["entered"] = True
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
            captured["exited"] = True
            return False

        def subscribe_to_new_messages(self, callback) -> None:
            captured["subscribed"] = True

        async def get_user_channels(self) -> list[object]:
            captured["channels_loaded"] = True
            return []

        async def run_until_disconnected(self) -> None:
            captured["waited"] = True
            return None

    monkeypatch.setattr("telegram_aggregator.processing.message_queue.MessageQueue", _FakeQueue)
    monkeypatch.setattr("telegram_aggregator.telegram.TelegramClient", _FakeClient)

    run_service()

    assert captured["dry_run"] is False
    assert captured["queue_run"] is True
    assert captured["subscribed"] is True
    assert captured["waited"] is True
    assert storage_events == [
        ("storage-build", "postgresql+asyncpg://user:pass@localhost:5432/app"),
        "storage-check",
        "storage-close",
    ]


def test_run_service_surfaces_unauthorized_session(
    set_service_env,
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="0", create_session_file=True)
    _install_fake_storage(monkeypatch, [])
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
    _install_fake_storage(monkeypatch, [])
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
    _install_fake_storage(monkeypatch, [])

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


def test_run_service_surfaces_storage_readiness_errors_cleanly(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        check_exception=StorageConfigError("DB unreachable: connection refused"),
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

    with pytest.raises(SystemExit, match="DB unreachable: connection refused"):
        run_service()

    assert events == [
        ("storage-build", "postgresql+asyncpg://user:pass@localhost:5432/app"),
        "client-init",
        "storage-check",
        "storage-close",
    ]
