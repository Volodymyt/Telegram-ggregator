"""Unit coverage for the canonical application config surface."""

from __future__ import annotations

from pathlib import Path

import pytest

from telegram_aggregator.bootstrap.login import run_login
from telegram_aggregator.bootstrap.service import run_service
from telegram_aggregator.config import AppConfigError, ConfigPathError, load_app_config
from telegram_aggregator.reading.telegram_client import TelegramClient

_VALID_CONFIG_YAML = """\
sources: []

filters:
  - mode: any
    include: []
    exclude: []
    case_insensitive: true
    normalize: true

repost:
  add_source_footer: true
  footer_template: "Source: {source}\\n{link}"
  fallback_on_copy_forbidden: "link_only"

runtime:
  processing_queue_size: 1000
  candidate_queue_size: 1000
  publish_queue_size: 200
  candidate_similarity_threshold: 0.82
  event_reopen_window_seconds: 300
  candidate_recovery_scan_seconds: 15
"""


@pytest.fixture(autouse=True)
def _disable_dotenv(monkeypatch) -> None:
    monkeypatch.setattr(
        "telegram_aggregator.config.app_config.load_dotenv",
        lambda *args, **kwargs: None,
    )


class _FakeTelethonClient:
    def __init__(self, *, authorized: bool = True, **kwargs) -> None:
        self.authorized = authorized
        self.kwargs = kwargs
        self.connect_calls = 0
        self.disconnect_calls = 0

    async def connect(self) -> None:
        self.connect_calls += 1

    async def disconnect(self) -> None:
        self.disconnect_calls += 1

    async def is_user_authorized(self) -> bool:
        return self.authorized


def _write_config_file(tmp_path: Path) -> Path:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(_VALID_CONFIG_YAML, encoding="utf-8")
    return config_path


def _set_service_env(
    monkeypatch,
    tmp_path: Path,
    *,
    config_path: str = "config.yaml",
    session_path: str = "sessions/default.session",
    dry_run: str | None = None,
) -> Path:
    config_file = _write_config_file(tmp_path)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TG_API_ID", "123")
    monkeypatch.setenv("TG_API_HASH", "hash")
    monkeypatch.setenv("TG_SESSION_PATH", session_path)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/app")
    monkeypatch.setenv("TARGET_CHANNEL", "@alerts")
    monkeypatch.setenv("CONFIG_PATH", config_path)

    if dry_run is None:
        monkeypatch.delenv("DRY_RUN", raising=False)
    else:
        monkeypatch.setenv("DRY_RUN", dry_run)

    return config_file


def test_load_app_config_resolves_relative_paths(monkeypatch, tmp_path: Path) -> None:
    config_file = _set_service_env(monkeypatch, tmp_path)

    config = load_app_config()

    assert config.telegram.session_path == (tmp_path / "sessions/default.session").resolve()
    assert config.config_path == config_file.resolve()
    assert config.file_config.sources == ()
    assert config.file_config.filters[0].mode == "any"
    assert config.file_config.runtime.candidate_similarity_threshold == pytest.approx(0.82)
    assert config.log_level == "INFO"
    assert config.dry_run is False


def test_load_app_config_rejects_invalid_api_id(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path)
    monkeypatch.setenv("TG_API_ID", "not-an-int")

    with pytest.raises(
        AppConfigError,
        match="Environment variable TG_API_ID must be a valid integer",
    ):
        load_app_config()


def test_load_app_config_rejects_missing_database_url(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(
        AppConfigError,
        match="Missing required environment variable: DATABASE_URL",
    ):
        load_app_config()


def test_load_app_config_rejects_missing_config_file(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path, config_path="missing.yaml")

    with pytest.raises(ConfigPathError, match="Config file does not exist:"):
        load_app_config()


def test_load_app_config_rejects_invalid_boolean(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path, dry_run="sometimes")

    with pytest.raises(
        AppConfigError,
        match="Environment variable DRY_RUN must be a boolean value",
    ):
        load_app_config()


def test_load_app_config_rejects_invalid_log_level(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path)
    monkeypatch.setenv("LOG_LEVEL", "verbose")

    with pytest.raises(
        AppConfigError,
        match="Environment variable LOG_LEVEL must be one of:",
    ):
        load_app_config()


def test_load_app_config_allows_blank_telegram_values_in_dry_run(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path, dry_run="1")
    monkeypatch.setenv("TG_API_ID", "   ")
    monkeypatch.setenv("TG_API_HASH", "   ")
    monkeypatch.setenv("TARGET_CHANNEL", "   ")

    config = load_app_config()

    assert config.dry_run is True
    assert config.telegram.api_id is None
    assert config.telegram.api_hash == ""
    assert config.target_channel == ""


def test_load_app_config_still_rejects_blank_target_channel_outside_dry_run(
    monkeypatch,
    tmp_path: Path,
) -> None:
    _set_service_env(monkeypatch, tmp_path, dry_run="0")
    monkeypatch.setenv("TARGET_CHANNEL", "   ")

    with pytest.raises(
        AppConfigError,
        match="Environment variable TARGET_CHANNEL must not be empty",
    ):
        load_app_config()


def test_run_service_exits_cleanly_on_missing_database_url(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(SystemExit, match="Missing required environment variable: DATABASE_URL"):
        run_service()


def test_run_service_exits_cleanly_on_invalid_log_level(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path)
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")

    with pytest.raises(SystemExit, match="Environment variable LOG_LEVEL must be one of:"):
        run_service()


def test_run_service_exits_cleanly_on_invalid_yaml_shape(monkeypatch, tmp_path: Path) -> None:
    config_file = _set_service_env(monkeypatch, tmp_path)
    config_file.write_text("sources: []\n", encoding="utf-8")

    with pytest.raises(
        SystemExit,
        match="Config section document root has invalid keys",
    ):
        run_service()


def test_run_service_dry_run_skips_telegram_runtime(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path, dry_run="1")
    events: list[object] = []

    class _FakeQueue:
        def run(self) -> None:
            events.append("queue-run")

        def push(self, message) -> None:
            events.append(("queue-push", message))

    class _FakeClient:
        def __init__(self, config, *, dry_run: bool = False) -> None:
            events.append(("client-init", dry_run, config.session_path))

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
    monkeypatch.setattr("telegram_aggregator.reading.telegram_client.TelegramClient", _FakeClient)

    run_service()

    assert events == [
        ("client-init", True, (tmp_path / "sessions/default.session").resolve()),
        "client-enter",
        "subscribe",
        "get-user-channels",
        "queue-run",
        "run-until-disconnected",
        "client-exit",
    ]


def test_run_service_uses_telegram_runtime_when_not_dry_run(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path, dry_run="0")
    captured: dict[str, object] = {}

    class _FakeQueue:
        def run(self) -> None:
            captured["queue_run"] = True

        def push(self, message) -> None:
            captured.setdefault("pushed", []).append(message)

    class _FakeClient:
        def __init__(self, config, *, dry_run: bool = False) -> None:
            captured["dry_run"] = dry_run
            captured["session_path"] = config.session_path

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
    monkeypatch.setattr("telegram_aggregator.reading.telegram_client.TelegramClient", _FakeClient)

    run_service()

    assert captured["dry_run"] is False
    assert captured["queue_run"] is True
    assert captured["subscribed"] is True
    assert captured["waited"] is True


def test_run_login_uses_canonical_startup_loader(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path)

    with pytest.raises(SystemExit, match="Resolved session path:") as exc_info:
        run_login()

    assert "Validated session path:" not in str(exc_info.value)


def test_run_login_respects_dry_run_contract(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path)
    monkeypatch.setenv("DRY_RUN", "1")
    monkeypatch.setattr(
        "telegram_aggregator.reading.telegram_client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("Telethon must not be touched in DRY_RUN")
        ),
    )

    with pytest.raises(
        SystemExit,
        match="Login bootstrap is disabled when DRY_RUN is enabled",
    ):
        run_login()


def test_run_login_surfaces_canonical_loader_errors(monkeypatch, tmp_path: Path) -> None:
    _set_service_env(monkeypatch, tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(SystemExit, match="Missing required environment variable: DATABASE_URL"):
        run_login()


@pytest.mark.asyncio
async def test_telegram_client_connects_with_existing_session(monkeypatch) -> None:
    fake_client = _FakeTelethonClient()

    def _build_client(**kwargs):
        fake_client.kwargs = kwargs
        return fake_client

    monkeypatch.setattr("telegram_aggregator.reading.telegram_client.telethon.TelegramClient", _build_client)

    client = TelegramClient(
        config=type("Settings", (), {
            "api_id": 123,
            "api_hash": "hash",
            "session_path": Path("/tmp/session.session"),
        })(),
    )

    async with client:
        pass

    assert fake_client.kwargs == {
        "session": "/tmp/session.session",
        "api_id": 123,
        "api_hash": "hash",
    }
    assert fake_client.connect_calls == 1
    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_telegram_client_dry_run_skips_telethon(monkeypatch) -> None:
    wait_calls: list[str] = []

    class _FakeEvent:
        async def wait(self) -> None:
            wait_calls.append("wait")
            return None

    monkeypatch.setattr(
        "telegram_aggregator.reading.telegram_client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("Telethon must not be constructed in dry-run mode")
        ),
    )
    monkeypatch.setattr("telegram_aggregator.reading.telegram_client.asyncio.Event", _FakeEvent)

    client = TelegramClient(
        config=type("Settings", (), {
            "api_id": 123,
            "api_hash": "hash",
            "session_path": Path("/tmp/session.session"),
        })(),
        dry_run=True,
    )

    async def _callback(message) -> None:
        return None

    async with client:
        handler = client.subscribe_to_new_messages(_callback)
        channels = await client.get_user_channels()
        history = await client.fetch_channel_history(123)
        client.unsubscribe_from_new_messages(handler)
        client.unsubscribe_all()

    await client.run_until_disconnected()

    assert channels == []
    assert history == []
    assert wait_calls == ["wait"]


@pytest.mark.asyncio
async def test_telegram_client_rejects_unauthorized_session(monkeypatch) -> None:
    fake_client = _FakeTelethonClient(authorized=False)

    monkeypatch.setattr(
        "telegram_aggregator.reading.telegram_client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(
        config=type("Settings", (), {
            "api_id": 123,
            "api_hash": "hash",
            "session_path": Path("/tmp/session.session"),
        })(),
    )

    with pytest.raises(
        RuntimeError,
        match="Telegram session is not authorized. Run `python -m telegram_aggregator.login` first.",
    ):
        async with client:
            pass

    assert fake_client.connect_calls == 1
    assert fake_client.disconnect_calls == 1
