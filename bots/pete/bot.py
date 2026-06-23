from __future__ import annotations

from aiogram.types import BotCommand
from core.config import BotConfig
from core.telegram_runtime import run_polling_bot
from shared.services.container import ServiceContainer

# Import Pete's custom router
from bots.pete.router import router as pete_router

async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    # These commands will automatically appear in the Telegram '/' menu
    commands = [
        BotCommand(command="warn", description="[Admin] Issue warning (-10 Trust Points)"),
        BotCommand(command="mute", description="[Admin] Revoke typing permissions (-20 Trust Points)"),
        BotCommand(command="kick", description="[Admin] Remove user from group (-30 Trust Points)"),
        BotCommand(command="ban", description="[Admin] Permanently ban user (-50 Trust Points)"),
        BotCommand(command="help", description="Show Pete's operating instructions")
    ]
    
    await run_polling_bot(
        config, 
        services, 
        description="High King Peter - Moderation & Security",
        router=pete_router,
        commands=commands
    )
