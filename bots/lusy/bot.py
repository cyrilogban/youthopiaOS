from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core.config import BotConfig
from core.telegram_runtime import build_router, run_polling_bot
from shared.services.container import ServiceContainer


def _router() -> Router:
    router = build_router("lusy", "Lusy games and XP bot")

    @router.message(Command("xp"))
    async def xp(message: Message, services: ServiceContainer) -> None:
        user = await services.identity.resolve_telegram_user(message.from_user)
        level = await services.xp.get_level(user["id"])
        await message.answer(f"XP: {level['total_xp']} | Level: {level['level']}")

    return router


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    await run_polling_bot(config, services, description="Lusy games and XP bot", router=_router())
