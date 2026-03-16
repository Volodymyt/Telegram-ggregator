"""Canonical configuration package surface."""

from telegram_aggregator.config.app_config import (
    AppConfig,
    AppConfigError,
    ConfigPathError,
    TelegramSessionSettings,
    load_app_config,
)

__all__ = [
    "AppConfig",
    "AppConfigError",
    "ConfigPathError",
    "TelegramSessionSettings",
    "load_app_config",
]
