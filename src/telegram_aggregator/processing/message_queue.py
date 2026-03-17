"""Temporary processing queue used by the existing service flow."""

from __future__ import annotations

import logging
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram_aggregator.telegram import MessageInfo

logger = logging.getLogger(__name__)


class MessageQueue:
    """Minimal in-process queue for the current bootstrap-compatible runtime."""

    def __init__(self) -> None:
        self._running = False
        self._queue: deque[MessageInfo] = deque()

    def push(self, message: MessageInfo) -> None:
        self._queue.append(message)

        if self._running:
            self._process_messages()

    def run(self) -> None:
        self._running = True
        self._process_messages()

    def stop(self) -> None:
        self._running = False

    def _process_messages(self) -> None:
        while self._queue:
            message = self._queue.popleft()
            logger.info(
                "[channel=%s] Process message id=%s text=%r attachment=%s",
                message.channel_tg_id,
                message.tg_id,
                (message.text or "")[:80],
                message.with_attachment,
            )
