from __future__ import annotations

from aiogram.types import BotCommand

from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer
from bots.theo.router import build_theo_router

# Commands that appear in Telegram's sidebar menu button
THEO_COMMANDS = [
    BotCommand(command="start", description="Meet Theo"),
    BotCommand(command="help", description="Show help information"),
    BotCommand(command="subscribe", description="Subscribe to daily verses"),
    BotCommand(command="unsubscribe", description="Unsubscribe from daily verses"),
]


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    router = build_theo_router(description="Theo devotional bot")
    await run_polling_bot(
        config,
        services,
        description="Theo devotional bot",
        router=router,
        commands=THEO_COMMANDS,
    )
