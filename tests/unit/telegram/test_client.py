"""Unit coverage for the Telethon-backed Telegram client adapter."""

from __future__ import annotations

import asyncio
import logging
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from telethon.errors import RPCError
from telethon.tl.types import Channel

from telegram_aggregator.telegram import (
    SessionAuthorizationError,
    SessionPathError,
    TelegramClient,
)
from telegram_aggregator.telegram.client import MessageInfo


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
    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("Telethon must not be constructed in dry-run mode")
        ),
    )
    monkeypatch.setattr(
        TelegramClient,
        "_wait_for_shutdown_signal",
        lambda self: asyncio.sleep(0),
    )

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
    caplog: pytest.LogCaptureFixture,
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

    with caplog.at_level(logging.WARNING, logger="telegram_aggregator.telegram.client"):
        with pytest.raises(
            SessionAuthorizationError,
            match="Telegram authorization failed: RPCError 400: AUTH_FAIL",
        ):
            await client.authorize_interactively()

    assert fake_client.disconnect_calls == 1

    warning_records = [
        r for r in caplog.records
        if r.levelno == logging.WARNING
        and "SessionPathError" in r.message
        and "disconnect" in r.message.lower()
    ]
    assert len(warning_records) == 1, (
        f"Expected exactly one suppressed-disconnect warning, got {len(warning_records)}"
    )


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


def _make_channel(*, tg_id: int, username: str, title: str, broadcast: bool) -> Channel:
    """Build a minimal Channel object for dialog testing."""
    return Channel(
        id=tg_id,
        title=title,
        photo=None,
        date=None,
        access_hash=0,
        username=username,
        broadcast=broadcast,
    )


def _make_dialog(entity: object) -> SimpleNamespace:
    return SimpleNamespace(entity=entity)


@pytest.mark.asyncio
async def test_get_user_channels_broadcast_only_filters_non_broadcast(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    broadcast_channel = _make_channel(
        tg_id=100, username="news", title="News", broadcast=True,
    )
    group_channel = _make_channel(
        tg_id=200, username="group", title="Group Chat", broadcast=False,
    )

    fake_client = fake_telethon_client_cls(
        dialogs=[_make_dialog(broadcast_channel), _make_dialog(group_channel)],
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    async with client:
        channels = await client.get_user_channels(broadcast_only=True)

    assert len(channels) == 1
    assert channels[0].tg_id == 100
    assert channels[0].username == "news"
    assert channels[0].title == "News"


@pytest.mark.asyncio
async def test_get_user_channels_broadcast_only_false_returns_all(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    broadcast_channel = _make_channel(
        tg_id=100, username="news", title="News", broadcast=True,
    )
    group_channel = _make_channel(
        tg_id=200, username="group", title="Group Chat", broadcast=False,
    )
    non_channel = SimpleNamespace(id=300, username="user", title="User")

    fake_client = fake_telethon_client_cls(
        dialogs=[
            _make_dialog(broadcast_channel),
            _make_dialog(group_channel),
            _make_dialog(non_channel),
        ],
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    async with client:
        channels = await client.get_user_channels(broadcast_only=False)

    assert len(channels) == 2
    tg_ids = {ch.tg_id for ch in channels}
    assert tg_ids == {100, 200}


@pytest.mark.asyncio
async def test_get_user_channels_skips_non_channel_dialogs(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    user_entity = SimpleNamespace(id=999, username="person", title="Person")

    fake_client = fake_telethon_client_cls(
        dialogs=[_make_dialog(user_entity)],
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    async with client:
        channels = await client.get_user_channels()

    assert channels == []


@pytest.mark.asyncio
async def test_subscribe_handler_invoked_on_new_message(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    """Verify the registered handler calls the user callback with a MessageInfo."""
    fake_client = fake_telethon_client_cls()

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    received: list[MessageInfo] = []

    async def _on_message(msg: MessageInfo) -> None:
        received.append(msg)

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    async with client:
        client.subscribe_to_new_messages(_on_message)

        assert len(fake_client.handlers) == 1
        _event_filter, handler_fn = fake_client.handlers[0]

        chat = _make_channel(
            tg_id=42, username="alerts", title="Alerts", broadcast=True,
        )

        message = SimpleNamespace(
            id=7,
            text="incoming alert",
            date=None,
            edit_date=None,
            media=None,
            views=10,
            forwards=2,
        )
        event = SimpleNamespace(
            get_chat=AsyncMock(return_value=chat),
            message=message,
        )

        await handler_fn(event)

    assert len(received) == 1
    info = received[0]
    assert info.tg_id == 7
    assert info.channel_tg_id == 42
    assert info.text == "incoming alert"
    assert info.with_attachment is False


@pytest.mark.asyncio
async def test_subscribe_handler_ignores_non_channel_chat(
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    runtime_config,
    tmp_path: Path,
) -> None:
    """Handler should silently skip events from non-Channel chats (e.g. users/groups)."""
    fake_client = fake_telethon_client_cls()

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    received: list[MessageInfo] = []

    async def _on_message(msg: MessageInfo) -> None:
        received.append(msg)

    client = TelegramClient(runtime_config(session_path=_create_session_file(tmp_path)))

    async with client:
        client.subscribe_to_new_messages(_on_message)

        _event_filter, handler_fn = fake_client.handlers[0]

        non_channel_chat = SimpleNamespace(id=99, title="Private")
        event = SimpleNamespace(
            get_chat=AsyncMock(return_value=non_channel_chat),
            message=SimpleNamespace(id=1, text="hello"),
        )

        await handler_fn(event)

    assert received == []
