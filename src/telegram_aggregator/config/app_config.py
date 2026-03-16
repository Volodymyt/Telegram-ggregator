"""Canonical application config loader and parsing helpers."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}
_VALID_LOG_LEVELS = tuple(sorted(logging.getLevelNamesMapping()))

if TYPE_CHECKING:
    from telegram_aggregator.config.file_config import FileConfig


@dataclass(frozen=True)
class TelegramSessionSettings:
    api_id: int | None
    api_hash: str
    session_path: Path


@dataclass(frozen=True)
class AppConfig:
    telegram: TelegramSessionSettings
    database_url: str
    target_channel: str
    config_path: Path
    file_config: FileConfig
    log_level: str
    dry_run: bool


class AppConfigError(ValueError):
    """Raised when application env input is missing or malformed."""


class ConfigPathError(AppConfigError):
    """Raised when CONFIG_PATH cannot be used as a config file."""


def load_app_config() -> AppConfig:
    """Load the canonical application config for bootstrap entrypoints."""

    from telegram_aggregator.config.file_config import load_file_config
    from telegram_aggregator.config.semantic_validation import validate_app_config

    load_dotenv()
    dry_run = _optional_bool_env("DRY_RUN", default=False)
    config_path = _validated_config_path(_required_path_env("CONFIG_PATH"))

    config = AppConfig(
        telegram=_load_telegram_session_settings(allow_empty=dry_run),
        database_url=_required_env("DATABASE_URL"),
        target_channel=_required_env("TARGET_CHANNEL", allow_empty=dry_run),
        config_path=config_path,
        file_config=load_file_config(config_path),
        log_level=_optional_log_level_env("LOG_LEVEL", default="INFO"),
        dry_run=dry_run,
    )

    validate_app_config(config)
    return config


def _load_telegram_session_settings(*, allow_empty: bool = False) -> TelegramSessionSettings:
    return TelegramSessionSettings(
        api_id=_required_int_env("TG_API_ID", allow_empty=allow_empty),
        api_hash=_required_env("TG_API_HASH", allow_empty=allow_empty),
        session_path=_required_path_env("TG_SESSION_PATH"),
    )


def _required_env(name: str, *, allow_empty: bool = False) -> str:
    value = os.getenv(name)

    if value is None:
        raise AppConfigError(f"Missing required environment variable: {name}")

    value = value.strip()

    if not value:
        if allow_empty:
            return ""

        raise AppConfigError(f"Environment variable {name} must not be empty")

    return value


def _required_int_env(name: str, *, allow_empty: bool = False) -> int | None:
    value = _required_env(name, allow_empty=allow_empty)

    if allow_empty and value == "":
        return None

    try:
        return int(value)
    except ValueError as exc:
        raise AppConfigError(
            f"Environment variable {name} must be a valid integer"
        ) from exc


def _required_path_env(name: str) -> Path:
    return _resolve_path(_required_env(name))


def _optional_text_env(name: str, *, default: str) -> str:
    value = os.getenv(name)

    if value is None:
        return default

    value = value.strip()

    if not value:
        raise AppConfigError(f"Environment variable {name} must not be empty")

    return value.upper()


def _optional_log_level_env(name: str, *, default: str) -> str:
    value = _optional_text_env(name, default=default)

    if value not in _VALID_LOG_LEVELS:
        allowed_levels = ", ".join(_VALID_LOG_LEVELS)
        raise AppConfigError(
            f"Environment variable {name} must be one of: {allowed_levels}"
        )

    return value


def _optional_bool_env(name: str, *, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().lower()

    if not normalized:
        raise AppConfigError(f"Environment variable {name} must not be empty")

    if normalized in _TRUE_VALUES:
        return True

    if normalized in _FALSE_VALUES:
        return False

    raise AppConfigError(
        f"Environment variable {name} must be a boolean value"
    )


def _resolve_path(value: str) -> Path:
    path = Path(value).expanduser()

    if not path.is_absolute():
        path = Path.cwd() / path

    return path.resolve(strict=False)


def _validated_config_path(path: Path) -> Path:
    if not path.exists():
        raise ConfigPathError(f"Config file does not exist: {path}")

    if not path.is_file():
        raise ConfigPathError(f"Config path must point to a file: {path}")

    return path
