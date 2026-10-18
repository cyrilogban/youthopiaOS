from __future__ import annotations

from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer
from bots.susy.router import build_susy_router


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    from aiogram.types import BotCommand

    susy_commands = [
        BotCommand(command="start", description="Meet Susan"),
        BotCommand(command="tour", description="Take the YouThopia community tour"),
        BotCommand(command="app", description="Open the YouThopia Mini App"),
        BotCommand(command="help", description="Show Susan hostess & community features"),
    ]

    susy_router = build_susy_router("Susan onboarding and engagement bot")

    await run_polling_bot(
        config, 
        services, 
        description="Susan onboarding and engagement bot",
        router=susy_router,
        commands=susy_commands,
    )
