from __future__ import annotations

from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    await run_polling_bot(config, services, description="Susy onboarding and engagement bot")
