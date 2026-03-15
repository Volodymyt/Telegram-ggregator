"""Temporary Telegram client wrapper behind the canonical reading package."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timezone
from typing import Awaitable, Callable

import telethon
from telethon import TelegramClient as TelethonClient, events
from telethon.tl.types import Channel, Message, MessageMediaDocument, MessageMediaPhoto

from telegram_aggregator.config.runtime import TGConfig

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

    def __init__(self, config: TGConfig) -> None:
        self._config = config
        self._client = telethon.TelegramClient(
            session=config.tg_session_path,
            api_id=config.tg_api_id,
            api_hash=config.tg_api_hash,
        )
        self._handlers: list[Callable[..., object]] = []

    async def __aenter__(self) -> TelegramClient:
        await self._client.start(phone=self._config.tg_phone)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self._client.disconnect()
        return False

    async def get_user_channels(self, *, broadcast_only: bool = True) -> list[ChannelInfo]:
        channels: list[ChannelInfo] = []

        async for dialog in self._client.iter_dialogs():
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
        entity = await self._client.get_entity(channel_tg_id)
        messages: list[MessageInfo] = []

        async for message in self._client.iter_messages(entity, limit=limit, min_id=min_id):
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
        @self._client.on(events.NewMessage)
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
        self._client.remove_event_handler(handler)
        self._handlers.remove(handler)
        logger.info(
            "unsubscribe_from_new_messages: handler removed (remaining=%d)",
            len(self._handlers),
        )

    def unsubscribe_all(self) -> None:
        for handler in list(self._handlers):
            self._client.remove_event_handler(handler)

        self._handlers.clear()
        logger.info("unsubscribe_all: all handlers removed")

    async def run_until_disconnected(self) -> None:
        await self._client.run_until_disconnected()
