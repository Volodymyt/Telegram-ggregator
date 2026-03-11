

class App:
    def __init__(self) -> None:
        self._client = TelegramClient()
        self._mq = MessageQueue()

    async def run(self) -> None:
        # Initialization
        self._client.subscribe_to_new_messages(self.on_new_message)
        logger.info("Listening for new messages")

        logger.info("Load channels...")
        channels = await client.get_user_channels()
        for ch in channels:
            logger.info("  channel • [%s] %s", ch.tg_id, ch.title)

        logger.info("Load history...")
        if channels:
            # TODO: fetch from all of needed channels
            messages = await client.fetch_channel_history(channels[0].tg_id, limit=50)
            for m in messages:
                # TODO: mb `_mq.push(m)` ?
                logger.info("  msg • id=%s date=%s text=%r", m.tg_id, m.date, (m.text or "")[:60])

        # Runtime
        _mq.run()

        await client.run_until_disconnected()

    async def on_new_message(self, msg: MessageInfo) -> None:
        self._mq.push(msg)
