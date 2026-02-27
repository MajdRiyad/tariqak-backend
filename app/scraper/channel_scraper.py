import logging
from datetime import datetime, timedelta, timezone
from app.scraper.telegram_client import get_telegram_client
from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)


async def scrape_channels():
    """Fetch new messages from all configured Telegram channels."""
    client = get_telegram_client()
    if not client.is_connected():
        await client.connect()

    db = await get_db()
    cutoff = datetime.now(timezone.utc) - timedelta(
        hours=settings.scrape_interval_hours + 1
    )
    total_new = 0

    for channel_name in settings.channel_list:
        try:
            entity = await client.get_entity(channel_name)
            messages = await client.get_messages(entity, limit=100)

            for msg in messages:
                if msg.text and msg.date >= cutoff:
                    await db.execute(
                        """INSERT OR IGNORE INTO messages
                           (channel_name, message_id, text, timestamp)
                           VALUES (?, ?, ?, ?)""",
                        (channel_name, msg.id, msg.text, msg.date.isoformat()),
                    )
                    total_new += 1

            await db.commit()
            logger.info(f"Scraped {channel_name}: processed messages")
        except Exception as e:
            logger.error(f"Error scraping {channel_name}: {e}")

    logger.info(f"Scrape complete. {total_new} new messages inserted.")
