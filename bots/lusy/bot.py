from __future__ import annotations

from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer
from bots.lusy.router import build_lusy_router


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    router = build_lusy_router(description="Lusy quizzes and XP bot")
    await run_polling_bot(config, services, description="Lusy quizzes and XP bot", router=router)
