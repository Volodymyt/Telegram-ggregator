import logging

from collections import deque
from telegram_aggregator.telegram.client import MessageInfo

logger = logging.getLogger(__name__)

class MessageQueue:

    def __init__(self) -> None:
        self._running: bool = False
        self._queue: deque[MessageInfo] = deque()

    def push(self, msg: MessageInfo) -> None:
        self._queue.append(msg)
        if self._running:
            self._process_messages()

    def run(self) -> None:
        self._running = True
        self._process_messages()

    def stop(self) -> None:
        self._running = False

    def _process_messages(self) -> None:
        while self._queue:
            msg = self._queue.popleft()
            # TODO:
            logger.info(
                "[channel=%s] Process message id=%s text=%r attachment=%s",
                msg.channel_tg_id, msg.tg_id, (msg.text or "")[:80], msg.with_attachment,
            )