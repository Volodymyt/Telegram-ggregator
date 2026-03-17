"""Unit coverage for the Telethon-backed Telegram client adapter."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from telethon.errors import RPCError

from telegram_aggregator.telegram import (
    SessionAuthorizationError,
    SessionPathError,
    TelegramClient,
)


def _create_session_file(tmp_path: Path) -> Path:
    session_path = tmp_path / "session.session"
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text("session", encoding="utf-8")
    return session_path


@pytest.mark.asyncio
async def test_telegram_client_connects_with_existing_session(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    fake_client = fake_telethon_client_cls()

    def _build_client(**kwargs):
        fake_client.kwargs = kwargs
        return fake_client

    monkeypatch.setattr("telegram_aggregator.telegram.client.telethon.TelegramClient", _build_client)

    session_path = _create_session_file(tmp_path)
    client = TelegramClient(runtime_config(session_path=session_path))

    async with client:
        pass

    assert fake_client.kwargs == {
        "session": str(session_path),
        "api_id": 123,
        "api_hash": "hash",
    }
    assert fake_client.connect_calls == 1
    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_telegram_client_dry_run_skips_telethon(
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
) -> None:
    wait_calls: list[str] = []

    class _FakeEvent:
        async def wait(self) -> None:
            wait_calls.append("wait")
            return None

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("Telethon must not be constructed in dry-run mode")
        ),
    )
    monkeypatch.setattr("telegram_aggregator.telegram.client.asyncio.Event", _FakeEvent)

    client = TelegramClient(runtime_config(dry_run=True))

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


def test_telegram_client_ensure_client_rejects_dry_run(
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
) -> None:
    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("Telethon must not be constructed in dry-run mode")
        ),
    )

    client = TelegramClient(runtime_config(dry_run=True))

    with pytest.raises(
        RuntimeError,
        match="Telethon client is not available in dry-run mode.",
    ):
        client._ensure_client()


@pytest.mark.asyncio
async def test_telegram_client_authorize_interactively_uses_explicit_callbacks(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
) -> None:
    fake_client = fake_telethon_client_cls()
    prompts = iter(["+380501234567", "12345"])

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )
    monkeypatch.setattr("builtins.input", lambda prompt: next(prompts))
    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.getpass.getpass",
        lambda prompt: "secret-password",
    )

    client = TelegramClient(runtime_config())

    await client.authorize_interactively()

    assert fake_client.start_calls == 1
    assert fake_client.prompt_values == {
        "phone": "+380501234567",
        "code": "12345",
        "password": "secret-password",
    }
    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_telegram_client_authorize_interactively_wraps_rpc_errors(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
) -> None:
    fake_client = fake_telethon_client_cls(
        start_exception=RPCError(request=None, message="AUTH_FAIL", code=400)
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config())

    with pytest.raises(
        SessionAuthorizationError,
        match="Telegram authorization failed: RPCError 400: AUTH_FAIL",
    ):
        await client.authorize_interactively()

    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_telegram_client_authorize_interactively_preserves_start_error_over_disconnect_error(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
) -> None:
    fake_client = fake_telethon_client_cls(
        start_exception=RPCError(request=None, message="AUTH_FAIL", code=400),
        disconnect_exception=sqlite3.OperationalError("unable to close database file"),
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config())

    with pytest.raises(
        SessionAuthorizationError,
        match="Telegram authorization failed: RPCError 400: AUTH_FAIL",
    ):
        await client.authorize_interactively()

    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_telegram_client_authorize_interactively_surfaces_disconnect_errors(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
) -> None:
    fake_client = fake_telethon_client_cls(
        disconnect_exception=sqlite3.OperationalError("unable to close database file"),
        start_uses_prompts=False,
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config())

    with pytest.raises(
        SessionPathError,
        match="Telegram session path is not usable: /tmp/session.session:",
    ):
        await client.authorize_interactively()

    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_telegram_client_authorize_interactively_wraps_build_session_path_errors(
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
) -> None:
    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            sqlite3.OperationalError("unable to open database file")
        ),
    )

    client = TelegramClient(runtime_config())

    with pytest.raises(
        SessionPathError,
        match="Telegram session path is not usable: /tmp/session.session:",
    ):
        await client.authorize_interactively()


@pytest.mark.asyncio
async def test_telegram_client_wraps_connect_session_path_errors(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    fake_client = fake_telethon_client_cls(
        connect_exception=sqlite3.OperationalError("unable to open database file")
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    with pytest.raises(
        SessionPathError,
        match=r"Telegram session path is not usable: .*/session\.session:",
    ):
        async with client:
            pass


@pytest.mark.asyncio
async def test_telegram_client_wraps_authorization_check_session_path_errors(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    fake_client = fake_telethon_client_cls(
        authorization_exception=sqlite3.OperationalError("database disk image is malformed")
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    with pytest.raises(
        SessionPathError,
        match="Telegram session path is not usable: .*database disk image is malformed",
    ):
        async with client:
            pass


@pytest.mark.asyncio
async def test_telegram_client_rejects_unauthorized_session(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    fake_client = fake_telethon_client_cls(authorized=False)

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    with pytest.raises(
        SessionAuthorizationError,
        match="Telegram session is not authorized. Run `python -m telegram_aggregator.login` first.",
    ):
        async with client:
            pass

    assert fake_client.connect_calls == 1
    assert fake_client.disconnect_calls == 1


@pytest.mark.asyncio
async def test_telegram_client_wraps_channel_discovery_session_path_errors(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    fake_client = fake_telethon_client_cls(
        dialog_iteration_exception=sqlite3.OperationalError("database disk image is malformed")
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    with pytest.raises(
        SessionPathError,
        match="Telegram session path is not usable: .*database disk image is malformed",
    ):
        async with client:
            await client.get_user_channels()


@pytest.mark.asyncio
async def test_telegram_client_wraps_get_entity_session_path_errors(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    fake_client = fake_telethon_client_cls(
        entity_exception=sqlite3.OperationalError("database disk image is malformed")
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    with pytest.raises(
        SessionPathError,
        match="Telegram session path is not usable: .*database disk image is malformed",
    ):
        async with client:
            await client.fetch_channel_history(123)


@pytest.mark.asyncio
async def test_telegram_client_wraps_history_iteration_session_path_errors(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    fake_client = fake_telethon_client_cls(
        message_iteration_exception=sqlite3.OperationalError("database disk image is malformed")
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    with pytest.raises(
        SessionPathError,
        match="Telegram session path is not usable: .*database disk image is malformed",
    ):
        async with client:
            await client.fetch_channel_history(123)


@pytest.mark.asyncio
async def test_telegram_client_wraps_run_until_disconnected_session_path_errors(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    fake_client = fake_telethon_client_cls(
        run_until_disconnected_exception=sqlite3.OperationalError(
            "database disk image is malformed"
        )
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    async with client:
        with pytest.raises(
            SessionPathError,
            match="Telegram session path is not usable: .*database disk image is malformed",
        ):
            await client.run_until_disconnected()
