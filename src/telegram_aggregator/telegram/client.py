"""Telethon-backed Telegram runtime adapter."""

from __future__ import annotations

import asyncio
import getpass
import inspect
import logging
import sqlite3
from dataclasses import dataclass
from datetime import timezone
from pathlib import Path
from typing import AsyncIterable, AsyncIterator, Awaitable, Callable, TypeVar, cast

import telethon
from telethon import TelegramClient as TelethonClient, events
from telethon.errors import RPCError
from telethon.tl.types import Channel, Message, MessageMediaDocument, MessageMediaPhoto

from telegram_aggregator.config import AppConfig, TelegramSessionSettings
from telegram_aggregator.telegram.errors import (
    SessionAuthorizationError,
    SessionPathError,
)

logger = logging.getLogger(__name__)


@dataclass
class ChannelInfo:
    tg_id: int
    username: str
    title: str


@dataclass
class MessageInfo:
    tg_id: int
    channel_tg_id: int
    text: str | None
    date: str
    edit_date: str | None
    with_attachment: bool
    media_type: str | None
    views: int | None
    forwards: int | None


def _has_attachment(message: Message) -> bool:
    return isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument))


def _to_utc(dt) -> str | None:
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat()


def _to_message_info(message: Message, channel_tg_id: int) -> MessageInfo:
    return MessageInfo(
        tg_id=message.id,
        channel_tg_id=channel_tg_id,
        text=message.text or None,
        date=_to_utc(message.date),
        edit_date=_to_utc(message.edit_date),
        with_attachment=_has_attachment(message),
        media_type=type(message.media).__name__ if message.media else None,
        views=message.views,
        forwards=message.forwards,
    )


MessageCallback = Callable[[MessageInfo], Awaitable[None]]
_T = TypeVar("_T")


def _reject_existing_non_file_session_path(path: Path) -> None:
    if not path.exists():
        return

    if path.is_dir():
        raise SessionPathError(
            f"Session path must point to a file, not a directory: {path}"
        )

    if not path.is_file():
        raise SessionPathError(f"Session path must point to a regular file: {path}")


def _reject_non_directory_parent(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise SessionPathError(f"Session path parent must be a directory: {path}")


def _ensure_session_parent_directory(parent: Path, session_path: Path) -> None:
    if parent.exists():
        return

    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SessionPathError(
            f"Could not create the session directory for {session_path}: {exc}"
        ) from exc


def _require_existing_session_parent_directory(parent: Path) -> None:
    if not parent.exists():
        raise SessionPathError(
            f"Session path parent directory does not exist: {parent}. "
            "Run `python -m telegram_aggregator.login` first."
        )


def _require_existing_session_file(path: Path) -> None:
    if not path.exists():
        raise SessionPathError(
            f"Telegram session file does not exist: {path}. "
            "Run `python -m telegram_aggregator.login` first."
        )


def _session_path_error(
        config: TelegramSessionSettings,
        exc: Exception,
) -> SessionPathError:
    return SessionPathError(
        f"Telegram session path is not usable: {config.session_path}: {exc}"
    )


class TelegramClient:
    """Thin Telethon adapter used by the current service bootstrap flow."""

    def __init__(self, config: AppConfig) -> None:
        self._session_settings = config.telegram
        self._dry_run = config.dry_run
        self._client: TelethonClient | None = None
        self._handlers: list[Callable[..., object]] = []

    def _skip_in_dry_run(self, message: str) -> bool:
        if not self._dry_run:
            return False

        logger.info(message)
        return True

    def _require_client(self) -> TelethonClient:
        if self._client is None:
            raise RuntimeError("Telegram client is not connected.")
        return self._client

    def _build_client(self) -> TelethonClient:
        if self._session_settings.api_id is None:
            raise RuntimeError("Telegram API ID is not configured.")

        try:
            return telethon.TelegramClient(
                session=str(self._session_settings.session_path),
                api_id=self._session_settings.api_id,
                api_hash=self._session_settings.api_hash,
            )
        except (OSError, sqlite3.Error) as exc:
            raise _session_path_error(self._session_settings, exc) from exc

    def _ensure_client(self) -> TelethonClient:
        if self._dry_run:
            raise RuntimeError("Telethon client is not available in dry-run mode.")

        if self._client is None:
            self._client = self._build_client()

        return self._client

    async def _connect(self) -> TelethonClient:
        client = self._ensure_client()
        await self._await_telethon_result(
            client.connect(),
            operation="connect()",
        )
        return client

    async def _disconnect(self) -> None:
        await self._await_telethon_result(
            self._require_client().disconnect(),
            operation="disconnect()",
        )

    def _prepare_existing_session(self) -> None:
        session_path = self._session_settings.session_path

        _reject_existing_non_file_session_path(session_path)
        _reject_non_directory_parent(session_path.parent)
        _require_existing_session_parent_directory(session_path.parent)
        _require_existing_session_file(session_path)

    def _prepare_writable_session(self) -> None:
        session_path = self._session_settings.session_path

        _reject_existing_non_file_session_path(session_path)
        _reject_non_directory_parent(session_path.parent)
        _ensure_session_parent_directory(session_path.parent, session_path)

    async def _await_telethon_result(
        self,
        result: Awaitable[_T],
        *,
        operation: str,
    ) -> _T:
        if not inspect.isawaitable(result):
            raise RuntimeError(
                f"Telethon {operation} did not return an awaitable in async context."
            )

        try:
            return await cast(Awaitable[_T], result)
        except (OSError, sqlite3.Error) as exc:
            raise _session_path_error(self._session_settings, exc) from exc

    async def _iterate_telethon_items(
        self,
        items: AsyncIterable[_T],
    ) -> AsyncIterator[_T]:
        try:
            async for item in items:
                yield item
        except (OSError, sqlite3.Error) as exc:
            raise _session_path_error(self._session_settings, exc) from exc

    @staticmethod
    def _prompt_phone() -> str:
        return input("Please enter your phone: ")

    @staticmethod
    def _prompt_code() -> str:
        return input("Please enter the code you received: ")

    @staticmethod
    def _prompt_password() -> str:
        return getpass.getpass("Please enter your password: ")

    async def __aenter__(self) -> TelegramClient:
        if self._skip_in_dry_run("DRY_RUN is enabled; Telegram client startup is skipped."):
            return self

        self._prepare_existing_session()
        client = await self._connect()

        if not await self._await_telethon_result(
            client.is_user_authorized(),
            operation="is_user_authorized()",
        ):
            await self._disconnect()
            raise SessionAuthorizationError(
                "Telegram session is not authorized. Run "
                "`python -m telegram_aggregator.login` first."
            )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._skip_in_dry_run("DRY_RUN is enabled; Telegram client shutdown is skipped."):
            return False

        await self._disconnect()
        return False

    async def authorize_interactively(self) -> None:
        if self._dry_run:
            raise SessionAuthorizationError(
                "Interactive authorization is not available in dry-run mode."
            )

        self._prepare_writable_session()
        client = self._ensure_client()
        primary_error: BaseException | None = None

        try:
            await self._await_telethon_result(
                client.start(
                    phone=self._prompt_phone,
                    password=self._prompt_password,
                    code_callback=self._prompt_code,
                ),
                operation="start()",
            )
        except SessionPathError as exc:
            primary_error = exc
        except RPCError as exc:
            primary_error = SessionAuthorizationError(
                f"Telegram authorization failed: {exc}"
            )
        except BaseException as exc:
            primary_error = exc
        finally:
            try:
                await self._disconnect()
            except SessionPathError as disconnect_exc:
                if primary_error is None:
                    raise
                logger.warning(
                    "secondary SessionPathError during disconnect suppressed "
                    "(primary error will propagate): %s",
                    disconnect_exc,
                )

        if primary_error is not None:
            raise primary_error

    async def get_user_channels(self, *, broadcast_only: bool = True) -> list[ChannelInfo]:
        if self._skip_in_dry_run("DRY_RUN is enabled; Telegram channel discovery is skipped."):
            return []

        client = self._require_client()
        channels: list[ChannelInfo] = []

        async for dialog in self._iterate_telethon_items(client.iter_dialogs()):
            entity = dialog.entity

            if not isinstance(entity, Channel):
                continue

            if broadcast_only and not entity.broadcast:
                continue

            channels.append(
                ChannelInfo(
                    tg_id=entity.id,
                    username=getattr(entity, "username", None) or str(entity.id),
                    title=entity.title,
                )
            )

        logger.info("get_user_channels: found %d channels", len(channels))
        return channels

    async def fetch_channel_history(
            self,
            channel_tg_id: int,
            *,
            limit: int = 100,
            min_id: int = 0,
    ) -> list[MessageInfo]:
        if self._skip_in_dry_run("DRY_RUN is enabled; Telegram history loading is skipped."):
            return []

        client = self._require_client()
        entity = await self._await_telethon_result(
            client.get_entity(channel_tg_id),
            operation="get_entity()",
        )
        messages: list[MessageInfo] = []

        async for message in self._iterate_telethon_items(
            client.iter_messages(entity, limit=limit, min_id=min_id)
        ):
            if not message.text and message.media is None:
                logger.debug(
                    "fetch_channel_history: skipping message with no text/media "
                    "(tg_msg_id=%s, channel_tg_id=%s)",
                    message.id,
                    channel_tg_id,
                )
                continue

            messages.append(_to_message_info(message, channel_tg_id))

        logger.info(
            "fetch_channel_history: got %d messages from channel %s",
            len(messages),
            channel_tg_id,
        )
        return messages

    def subscribe_to_new_messages(self, callback: MessageCallback) -> Callable[..., object]:
        if self._dry_run:
            self._handlers.append(callback)
            self._skip_in_dry_run("DRY_RUN is enabled; Telegram subscription is skipped.")
            return callback

        client = self._require_client()

        async def _handler(event: events.NewMessage.Event) -> None:
            chat = await event.get_chat()

            if not isinstance(chat, Channel):
                return

            message_info = _to_message_info(event.message, chat.id)
            logger.debug(
                "new message from '%s' (tg_msg_id=%s)",
                chat.title,
                event.message.id,
            )
            await callback(message_info)

        self._handlers.append(_handler)
        client.add_event_handler(_handler, events.NewMessage)
        logger.info(
            "subscribe_to_new_messages: handler registered (total=%d)",
            len(self._handlers),
        )
        return _handler

    def unsubscribe_from_new_messages(self, handler: Callable[..., object]) -> None:
        if self._dry_run:
            self._handlers.remove(handler)
            logger.info(
                "unsubscribe_from_new_messages: dry-run handler removed (remaining=%d)",
                len(self._handlers),
            )
            return

        self._require_client().remove_event_handler(handler)
        self._handlers.remove(handler)
        logger.info(
            "unsubscribe_from_new_messages: handler removed (remaining=%d)",
            len(self._handlers),
        )

    def unsubscribe_all(self) -> None:
        if self._skip_in_dry_run("unsubscribe_all: dry-run handlers cleared"):
            self._handlers.clear()
            return

        client = self._require_client()
        for handler in list(self._handlers):
            client.remove_event_handler(handler)

        self._handlers.clear()
        logger.info("unsubscribe_all: all handlers removed")

    async def run_until_disconnected(self) -> None:
        if self._skip_in_dry_run("DRY_RUN is enabled; Telegram transport not started."):
            return

        await self._await_telethon_result(
            self._require_client().run_until_disconnected(),
            operation="run_until_disconnected()",
        )
