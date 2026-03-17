"""Telegram integration subsystem."""

from telegram_aggregator.telegram.client import ChannelInfo, MessageInfo, TelegramClient
from telegram_aggregator.telegram.errors import (
    SessionAuthorizationError,
    SessionBootstrapError,
    SessionPathError,
)

__all__ = [
    "ChannelInfo",
    "MessageInfo",
    "SessionAuthorizationError",
    "SessionBootstrapError",
    "SessionPathError",
    "TelegramClient",
]
