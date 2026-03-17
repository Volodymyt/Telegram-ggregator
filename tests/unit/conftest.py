"""Shared fixtures and helpers for unit tests."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

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

_SEMANTIC_VALID_CONFIG_YAML = """\
sources:
  - "@channel1"
  - "https://t.me/channel2"
  - "-1001234567890"

filters:
  - mode: any
    include:
      - pattern: "alert"
        event_type: ballistic
        event_signal: start
    exclude: []
    case_insensitive: true
    normalize: true
  - mode: all
    include:
      - pattern: "drone"
        event_type: drone
        event_signal: start
      - pattern: "shahed"
        event_type: drone
        event_signal: start
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
def disable_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "telegram_aggregator.config.app_config.load_dotenv",
        lambda *args, **kwargs: None,
    )


@pytest.fixture
def valid_config_yaml() -> str:
    return _VALID_CONFIG_YAML


@pytest.fixture
def semantic_valid_config_yaml() -> str:
    return _SEMANTIC_VALID_CONFIG_YAML


def _write_config_file(tmp_path: Path, content: str) -> Path:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


@pytest.fixture
def set_service_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    valid_config_yaml: str,
):
    def _set_service_env(
        *,
        config_path: str = "config.yaml",
        session_path: str = "sessions/default.session",
        config_content: str = valid_config_yaml,
        target_channel: str = "@alerts",
        dry_run: str | None = None,
        create_session_file: bool = False,
    ) -> Path:
        config_file = _write_config_file(tmp_path, content=config_content)
        resolved_session_path = (tmp_path / session_path).resolve()

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("TG_API_ID", "123")
        monkeypatch.setenv("TG_API_HASH", "hash")
        monkeypatch.setenv("TG_SESSION_PATH", session_path)
        monkeypatch.setenv(
            "DATABASE_URL",
            "postgresql+asyncpg://user:pass@localhost:5432/app",
        )
        monkeypatch.setenv("TARGET_CHANNEL", target_channel)
        monkeypatch.setenv("CONFIG_PATH", config_path)

        if dry_run is None:
            monkeypatch.delenv("DRY_RUN", raising=False)
        else:
            monkeypatch.setenv("DRY_RUN", dry_run)

        if create_session_file:
            resolved_session_path.parent.mkdir(parents=True, exist_ok=True)
            resolved_session_path.write_text("session", encoding="utf-8")

        return config_file

    return _set_service_env


@pytest.fixture
def runtime_config():
    def _runtime_config(
        *,
        session_path: str | Path = "/tmp/session.session",
        dry_run: bool = False,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            telegram=SimpleNamespace(
                api_id=123,
                api_hash="hash",
                session_path=Path(session_path),
            ),
            dry_run=dry_run,
        )

    return _runtime_config


class FakeTelethonClient:
    def __init__(
        self,
        *,
        authorized: bool = True,
        authorization_exception: Exception | None = None,
        connect_exception: Exception | None = None,
        disconnect_exception: Exception | None = None,
        dialog_iteration_exception: Exception | None = None,
        entity_exception: Exception | None = None,
        message_iteration_exception: Exception | None = None,
        run_until_disconnected_exception: Exception | None = None,
        start_exception: Exception | None = None,
        start_uses_prompts: bool = True,
        dialogs: list[object] | None = None,
        entity: object | None = None,
        messages: list[object] | None = None,
        **kwargs,
    ) -> None:
        self.authorized = authorized
        self.authorization_exception = authorization_exception
        self.connect_exception = connect_exception
        self.disconnect_exception = disconnect_exception
        self.dialog_iteration_exception = dialog_iteration_exception
        self.entity_exception = entity_exception
        self.message_iteration_exception = message_iteration_exception
        self.run_until_disconnected_exception = run_until_disconnected_exception
        self.start_exception = start_exception
        self.start_uses_prompts = start_uses_prompts
        self.dialogs = dialogs or []
        self.entity = entity
        self.messages = messages or []
        self.kwargs = kwargs
        self.connect_calls = 0
        self.disconnect_calls = 0
        self.authorization_calls = 0
        self.get_entity_calls = 0
        self.run_until_disconnected_calls = 0
        self.start_calls = 0
        self.start_kwargs: dict[str, object] | None = None
        self.prompt_values: dict[str, str] = {}
        self.handlers: list[object] = []

    async def connect(self) -> None:
        self.connect_calls += 1

        if self.connect_exception is not None:
            raise self.connect_exception

    async def disconnect(self) -> None:
        self.disconnect_calls += 1

        if self.disconnect_exception is not None:
            raise self.disconnect_exception

    async def is_user_authorized(self) -> bool:
        self.authorization_calls += 1

        if self.authorization_exception is not None:
            raise self.authorization_exception

        return self.authorized

    async def start(self, **kwargs) -> None:
        self.start_calls += 1
        self.start_kwargs = kwargs

        if self.start_exception is not None:
            raise self.start_exception

        if not self.start_uses_prompts:
            return

        phone = kwargs["phone"]
        code_callback = kwargs["code_callback"]
        password = kwargs["password"]

        assert callable(phone)
        assert callable(code_callback)
        assert callable(password)

        self.prompt_values = {
            "phone": phone(),
            "code": code_callback(),
            "password": password(),
        }

    def iter_dialogs(self):
        async def _iterate():
            if self.dialog_iteration_exception is not None:
                raise self.dialog_iteration_exception

            for dialog in self.dialogs:
                yield dialog

        return _iterate()

    async def get_entity(self, channel_tg_id: int) -> object:
        self.get_entity_calls += 1

        if self.entity_exception is not None:
            raise self.entity_exception

        if self.entity is not None:
            return self.entity

        return channel_tg_id

    def iter_messages(self, entity, *, limit: int, min_id: int):
        async def _iterate():
            if self.message_iteration_exception is not None:
                raise self.message_iteration_exception

            for message in self.messages:
                yield message

        return _iterate()

    async def run_until_disconnected(self) -> None:
        self.run_until_disconnected_calls += 1

        if self.run_until_disconnected_exception is not None:
            raise self.run_until_disconnected_exception

    def on(self, event) -> object:
        def _decorator(handler):
            self.handlers.append((event, handler))
            return handler

        return _decorator

    def remove_event_handler(self, handler) -> None:
        self.handlers = [
            registered
            for registered in self.handlers
            if registered[1] is not handler
        ]


@pytest.fixture
def fake_telethon_client_cls() -> type[FakeTelethonClient]:
    return FakeTelethonClient
