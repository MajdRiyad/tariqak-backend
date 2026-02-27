import asyncio
import logging
from app.scraper.channel_scraper import scrape_channels
from app.config import settings

logger = logging.getLogger(__name__)
_task: asyncio.Task | None = None


async def _scrape_loop():
    """Background loop that scrapes channels on a regular interval."""
    while True:
        await asyncio.sleep(settings.scrape_interval_hours * 3600)
        try:
            logger.info("Starting scheduled scrape...")
            await scrape_channels()
            logger.info("Scheduled scrape completed.")
        except Exception as e:
            logger.error(f"Scheduled scrape failed: {e}")


async def start_scheduler():
    """Start the background scraper. Runs an initial scrape, then loops."""
    global _task
    if settings.telegram_api_id and settings.telegram_string_session:
        logger.info("Running initial scrape on startup...")
        try:
            await scrape_channels()
        except Exception as e:
            logger.error(f"Initial scrape failed (will retry on schedule): {e}")
        _task = asyncio.create_task(_scrape_loop())
        logger.info(
            f"Scraper scheduled every {settings.scrape_interval_hours} hours."
        )
    else:
        logger.warning(
            "Telegram credentials not configured. Scraper disabled. "
            "Use seed_test_data.py to populate test data."
        )


async def stop_scheduler():
    """Cancel the background scraper task."""
    global _task
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        logger.info("Scraper scheduler stopped.")
