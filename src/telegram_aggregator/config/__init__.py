"""Canonical configuration package surface."""

from telegram_aggregator.config.app_config import (
    AppConfig,
    AppConfigError,
    ConfigPathError,
    TelegramSessionSettings,
    load_app_config,
)
from telegram_aggregator.config.file_config import (
    FileConfig,
    FileConfigError,
    FilterGroupConfig,
    IncludeRuleConfig,
    RepostConfig,
    RuntimeConfig,
    load_file_config,
)

__all__ = [
    "AppConfig",
    "AppConfigError",
    "ConfigPathError",
    "FileConfig",
    "FileConfigError",
    "FilterGroupConfig",
    "IncludeRuleConfig",
    "RepostConfig",
    "RuntimeConfig",
    "TelegramSessionSettings",
    "load_app_config",
    "load_file_config",
]
