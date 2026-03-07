import asyncio
import logging

from telegram_aggregator.telegram.client import MessageInfo, TelegramAggregatorClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

async def on_new_message(msg: MessageInfo) -> None:
    logger.info(
        "[channel=%s] new message id=%s text=%r attachment=%s",
        msg.channel_tg_id, msg.tg_id, (msg.text or "")[:80], msg.with_attachment,
    )

async def main() -> None:
    async with TelegramAggregatorClient() as client:

        channels = await client.get_user_channels()
        for ch in channels:
            logger.info("  channel • [%s] %s", ch.tg_id, ch.title)

        if channels:
            messages = await client.fetch_channel_history(channels[0].tg_id, limit=50)
            for m in messages:
                logger.info("  msg • id=%s date=%s text=%r", m.tg_id, m.date, (m.text or "")[:60])

        client.subscribe_to_new_messages(on_new_message)
        logger.info("Listening for new messages (Ctrl+C to stop)...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())