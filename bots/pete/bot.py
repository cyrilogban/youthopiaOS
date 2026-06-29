from __future__ import annotations

from aiogram.types import BotCommand
from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer

# Import Pete's custom router
from bots.pete.router import router as pete_router

async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    await run_polling_bot(
        config, 
        services, 
        description="High King Peter - Moderation & Security",
        router=pete_router
    )
