"""Canonical login bootstrap entrypoint."""

from __future__ import annotations

import asyncio
import logging

from telegram_aggregator.config import AppConfigError, load_app_config
from telegram_aggregator.telegram import (
    SessionAuthorizationError,
    SessionPathError,
    TelegramClient,
)

logger = logging.getLogger(__name__)


def run_login() -> None:
    """Route login startup through the canonical bootstrap boundary."""

    try:
        config = load_app_config()
    except AppConfigError as exc:
        raise SystemExit(str(exc)) from None

    if config.dry_run:
        raise SystemExit(
            "Login bootstrap is disabled when DRY_RUN is enabled because "
            "Telegram I/O is not allowed in dry-run mode."
        )

    try:
        client = TelegramClient(config)
        asyncio.run(client.authorize_interactively())
    except (SessionAuthorizationError, SessionPathError) as exc:
        raise SystemExit(str(exc)) from None
    except Exception as exc:
        logger.error("Login failed: %s", exc)
        raise SystemExit(1) from None
