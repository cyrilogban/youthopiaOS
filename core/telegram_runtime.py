from __future__ import annotations

import os
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import BotCommand, Chat, ChatMemberUpdated, Message, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, BotCommandScopeAllChatAdministrators, BotCommandScopeChat

from core.config import BotConfig
from core.admin_commands import create_admin_router
from shared.logging.logger import get_logger
from shared.services.container import ServiceContainer


DEFAULT_BOT_SETTINGS = {
    "theo": {"translation": "kjv"},
    "lusy": {},
    "pete": {},
    "eddy": {},
    "susy": {},
}


async def register_chat(
    chat_obj: Chat,
    services: ServiceContainer,
    bot_name: str = "",
) -> dict | None:
    if chat_obj.type not in {"group", "supergroup"}:
        return None

    chat = await services.chats.upsert_chat(
        chat_obj.id,
        chat_obj.type,
        title=chat_obj.title,
        username=chat_obj.username,
    )
    if bot_name:
        await services.chats.mark_bot_active(bot_name, chat["id"])
        existing_settings = await services.supabase.find_one_multi(
            "chat_bot_settings", {"bot_name": bot_name, "chat_id": chat["id"]}
        )
        if not existing_settings:
            await services.chats.set_bot_settings(
                bot_name,
                chat["id"],
                DEFAULT_BOT_SETTINGS.get(bot_name, {}),
            )
        if bot_name == "theo":
            try:
                existing_sub = await services.chats.get_subscription("theo", chat["id"], "daily_devotional")
                if not existing_sub:
                    await services.chats.set_subscription(
                        bot_name="theo",
                        chat_id=chat["id"],
                        subscription_type="daily_devotional",
                        enabled=True,
                    )
            except Exception:
                pass
    return chat


async def register_group_chat(
    message: Message,
    services: ServiceContainer,
    bot_name: str,
) -> dict | None:
    return await register_chat(message.chat, services, bot_name)


def build_router(bot_name: str, description: str, *, include_base_commands: bool = True) -> Router:
    router = Router(name=bot_name)
    if bot_name.lower() == "eddy":
        router.include_router(create_admin_router(bot_name))

    if include_base_commands:
        @router.message(Command("start"))
        async def start(message: Message, services: ServiceContainer) -> None:
            await register_group_chat(message, services, bot_name)
            await message.answer(f"{description} is connected to YouThopiaOS.")

        @router.message(Command("profile"))
        async def profile(message: Message, services: ServiceContainer) -> None:
            await register_group_chat(message, services, bot_name)
            user = await services.identity.resolve_telegram_user(message.from_user)
            await message.answer(
                "Your Community profile is active.\n"
                f"Level: {user.get('level', 1)}\n"
                f"XP: {user.get('total_xp', 0)}\n"
                f"Trust: {user.get('trust_score', 100)}"
            )

    # Fallback sub-router for default group tracking
    _fallback = Router(name=f"{bot_name}_fallback")

    @_fallback.message()
    async def track_group(message: Message, services: ServiceContainer) -> None:
        try:
            await register_group_chat(message, services, bot_name)
        except Exception as e:
            logger.warning(f"Failed to register group chat for {bot_name}: {e}")

    router.include_router(_fallback)

    return router


async def run_polling_bot(
    config: BotConfig,
    services: ServiceContainer,
    *,
    description: str,
    router: Router | None = None,
    commands: list[BotCommand] | None = None,
) -> None:
    logger = get_logger(f"youthopia.{config.name}")
    bot = Bot(token=config.token)
    dispatcher = Dispatcher()
    dispatcher["services"] = services
    print(f"DEBUG: run_polling_bot for '{config.name}' received router: {router}")
    dispatcher.include_router(router or build_router(config.name, description))

    if commands:
        try:
            await bot.set_my_commands(commands)
            logger.info("Registered %d base menu commands for %s.", len(commands), config.name)
        except Exception:
            pass

    logger.info("Starting %s bot polling.", config.name)
    await dispatcher.start_polling(
        bot,
        allowed_updates=["message", "callback_query", "my_chat_member", "chat_member"]
    )
