from __future__ import annotations

from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer
from bots.susy.router import build_susy_router


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    susy_router = build_susy_router("Susy onboarding and engagement bot")
    await run_polling_bot(
        config, 
        services, 
        description="Susy onboarding and engagement bot",
        router=susy_router
    )
