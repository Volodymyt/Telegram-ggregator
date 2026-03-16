"""Temporary Telegram client wrapper behind the canonical reading package."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timezone
from typing import Awaitable, Callable

import telethon
from telethon import TelegramClient as TelethonClient, events
from telethon.tl.types import Channel, Message, MessageMediaDocument, MessageMediaPhoto

from telegram_aggregator.config import TelegramSessionSettings

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


class TelegramClient:
    """Thin Telethon adapter used by the current service bootstrap flow."""

    def __init__(self, config: TelegramSessionSettings, *, dry_run: bool = False) -> None:
        self._config = config
        self._dry_run = dry_run
        self._client: TelethonClient | None = None
        self._handlers: list[Callable[..., object]] = []

        if not dry_run:
            assert config.api_id is not None
            self._client = telethon.TelegramClient(
                session=str(config.session_path),
                api_id=config.api_id,
                api_hash=config.api_hash,
            )

    def _skip_in_dry_run(self, message: str) -> bool:
        if not self._dry_run:
            return False

        logger.info(message)
        return True

    def _require_client(self) -> TelethonClient:
        assert self._client is not None
        return self._client

    async def __aenter__(self) -> TelegramClient:
        if self._skip_in_dry_run("DRY_RUN is enabled; Telegram client startup is skipped."):
            return self

        client = self._require_client()
        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()
            raise RuntimeError(
                "Telegram session is not authorized. Run "
                "`python -m telegram_aggregator.login` first."
            )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._skip_in_dry_run("DRY_RUN is enabled; Telegram client shutdown is skipped."):
            return False

        await self._require_client().disconnect()
        return False

    async def get_user_channels(self, *, broadcast_only: bool = True) -> list[ChannelInfo]:
        if self._skip_in_dry_run("DRY_RUN is enabled; Telegram channel discovery is skipped."):
            return []

        client = self._require_client()
        channels: list[ChannelInfo] = []

        async for dialog in client.iter_dialogs():
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
        entity = await client.get_entity(channel_tg_id)
        messages: list[MessageInfo] = []

        async for message in client.iter_messages(entity, limit=limit, min_id=min_id):
            if not message.text and message.media is None:
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

        @client.on(events.NewMessage)
        async def _handler(event: events.NewMessage.Event) -> None:
            chat = await event.get_chat()

            if not isinstance(chat, Channel):
                return

            message_info = _to_message_info(event.message, chat.id)
            logger.debug(
                "New message from '%s' (tg_msg_id=%s)",
                chat.title,
                event.message.id,
            )
            await callback(message_info)

        self._handlers.append(_handler)
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
        if self._skip_in_dry_run("DRY_RUN is enabled; waiting without Telegram transport."):
            await asyncio.Event().wait()
            return

        await self._require_client().run_until_disconnected()
