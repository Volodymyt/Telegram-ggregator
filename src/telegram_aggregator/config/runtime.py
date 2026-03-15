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


def load_runtime_config() -> RuntimeConfig:
    """Load the temporary runtime configuration used by the existing service flow."""

    from dotenv import load_dotenv

    load_dotenv()

    return RuntimeConfig(
        telegram=TGConfig(
            tg_api_id=int(os.environ["TG_API_ID"]),
            tg_api_hash=os.environ["TG_API_HASH"],
            tg_phone=os.environ["TG_PHONE"],
            tg_session_path=os.environ["TG_SESSION_PATH"],
        ),
        logging=LoggingConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        ),
    )
