"""Temporary runtime configuration surface behind the canonical package layout."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LoggingConfig:
    level: int
    format: str


@dataclass(frozen=True)
class TGConfig:
    tg_api_id: int
    tg_api_hash: str
    tg_phone: str
    tg_session_path: str


@dataclass(frozen=True)
class RuntimeConfig:
    telegram: TGConfig
    logging: LoggingConfig


class RuntimeConfigError(ValueError):
    """Raised when the runtime env contract is missing or malformed."""


def load_runtime_config() -> RuntimeConfig:
    """Load the temporary runtime configuration used by the existing service flow."""

    from dotenv import load_dotenv

    load_dotenv()

    return RuntimeConfig(
        telegram=TGConfig(
            tg_api_id=_required_int_env("TG_API_ID"),
            tg_api_hash=_required_env("TG_API_HASH"),
            tg_phone=_required_env("TG_PHONE"),
            tg_session_path=_required_env("TG_SESSION_PATH"),
        ),
        logging=LoggingConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        ),
    )


def _required_env(name: str) -> str:
    """Return a normalized required env value."""

    value = os.getenv(name)

    if value is None:
        raise RuntimeConfigError(f"Missing required environment variable: {name}")

    value = value.strip()

    if not value:
        raise RuntimeConfigError(f"Environment variable {name} must not be empty")

    return value


def _required_int_env(name: str) -> int:
    """Parse a required integer env value."""

    value = _required_env(name)

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeConfigError(
            f"Environment variable {name} must be a valid integer"
        ) from exc
