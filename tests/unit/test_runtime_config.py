"""Unit coverage for the temporary runtime config surface."""

from __future__ import annotations

import pytest

from telegram_aggregator.bootstrap.service import run_service
from telegram_aggregator.config.runtime import TGConfig, RuntimeConfigError, load_runtime_config
from telegram_aggregator.reading.telegram_client import TelegramClient


class _FakeTelethonClient:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.start_calls: list[dict[str, object]] = []

    async def start(self, **kwargs) -> None:
        self.start_calls.append(kwargs)

    async def disconnect(self) -> None:
        return None


def test_load_runtime_config_requires_phone(monkeypatch) -> None:
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setenv("TG_API_ID", "123")
    monkeypatch.setenv("TG_API_HASH", "hash")
    monkeypatch.setenv("TG_SESSION_PATH", "/tmp/session.session")
    monkeypatch.delenv("TG_PHONE", raising=False)

    with pytest.raises(RuntimeConfigError, match="Missing required environment variable: TG_PHONE"):
        load_runtime_config()


def test_load_runtime_config_rejects_blank_phone(monkeypatch) -> None:
    monkeypatch.setenv("TG_API_ID", "123")
    monkeypatch.setenv("TG_API_HASH", "hash")
    monkeypatch.setenv("TG_SESSION_PATH", "/tmp/session.session")
    monkeypatch.setenv("TG_PHONE", "   ")

    with pytest.raises(RuntimeConfigError, match="Environment variable TG_PHONE must not be empty"):
        load_runtime_config()


def test_run_service_exits_cleanly_on_missing_phone(monkeypatch) -> None:
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setenv("TG_API_ID", "123")
    monkeypatch.setenv("TG_API_HASH", "hash")
    monkeypatch.setenv("TG_SESSION_PATH", "/tmp/session.session")
    monkeypatch.delenv("TG_PHONE", raising=False)

    with pytest.raises(SystemExit, match="Missing required environment variable: TG_PHONE"):
        run_service()


@pytest.mark.asyncio
async def test_telegram_client_start_passes_phone(monkeypatch) -> None:
    fake_client = _FakeTelethonClient()

    monkeypatch.setattr(
        "telegram_aggregator.reading.telegram_client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(
        TGConfig(
            tg_api_id=123,
            tg_api_hash="hash",
            tg_phone="+10000000000",
            tg_session_path="/tmp/session.session",
        )
    )

    async with client:
        pass

    assert fake_client.start_calls == [{"phone": "+10000000000"}]
