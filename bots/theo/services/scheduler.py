from __future__ import annotations

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from shared.services.container import ServiceContainer
from bots.theo.services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)


async def trigger_daily_votd(bot: Bot, services: ServiceContainer) -> dict:
    """Triggers the daily Verse of the Day broadcast to all subscribers."""
    try:
        delivery_service = DeliveryService(bot=bot, services=services)
        result = await delivery_service.broadcast_votd()
        logger.info(f"Theo VOTD Daily Broadcast Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error executing Theo VOTD Daily Broadcast: {e}")
        return {"status": "error", "message": str(e)}


def setup_theo_scheduler(bot: Bot, services: ServiceContainer) -> AsyncIOScheduler:
    """Initializes the APScheduler for Theo's 6:00 AM WAT Daily Verse broadcast."""
    scheduler = AsyncIOScheduler(timezone="Africa/Lagos")
    
    scheduler.add_job(
        trigger_daily_votd,
        CronTrigger(hour=6, minute=0, timezone="Africa/Lagos"),
        args=[bot, services]
    )
    
    scheduler.start()
    logger.info("Theo's 6:00 AM WAT Daily Verse scheduler has started.")
    return scheduler
