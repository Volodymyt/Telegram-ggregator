from collections import deque

class MessageQueue:
    _running: bool = False
    _queue: deque = deque()

    def push(self, msg: MessageInfo) -> None:
        _queue.append(msg)
        if (_running) {
            _self.processMessages()
        }

    def run(self) -> None:
        self._running = True
        _self.processMessages()

    def stop(self) -> None:
        self._running = False


    def processMessages() -> None:
        while msg = _queue.popleft() do:
            # TODO:
            logger.info(
                "[channel=%s] Process message id=%s text=%r attachment=%s",
                msg.channel_tg_id, msg.tg_id, (msg.text or "")[:80], msg.with_attachment,
            )
