import asyncio
import logging
import app

from telegram_aggregator.config import config

logging.basicConfig(
    level=config.logging.level,
    format=config.logging.format,
)
logger = logging.getLogger(__name__)

async def main() -> None:
    await App().run()

if __name__ == "__main__":
    asyncio.run(main())