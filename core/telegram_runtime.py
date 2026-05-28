from __future__ import annotations

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Chat, ChatMemberUpdated, Message

from core.config import BotConfig
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
    bot_name: str,
) -> dict | None:
    if chat_obj.type not in {"group", "supergroup"}:
        return None

    chat = await services.chats.upsert_chat(
        chat_obj.id,
        chat_obj.type,
        title=chat_obj.title,
        username=chat_obj.username,
    )
    await services.chats.mark_bot_active(bot_name, chat["id"])
    await services.chats.set_bot_settings(
        bot_name,
        chat["id"],
        DEFAULT_BOT_SETTINGS.get(bot_name, {}),
    )
    return chat


async def register_group_chat(
    message: Message,
    services: ServiceContainer,
    bot_name: str,
) -> dict | None:
    return await register_chat(message.chat, services, bot_name)


def build_router(bot_name: str, description: str) -> Router:
    router = Router(name=bot_name)

    @router.message(Command("start"))
    async def start(message: Message, services: ServiceContainer) -> None:
        await register_group_chat(message, services, bot_name)
        await message.answer(f"{description} is connected to YouThopiaOS.")

    @router.message(Command("profile"))
    async def profile(message: Message, services: ServiceContainer) -> None:
        await register_group_chat(message, services, bot_name)
        user = await services.identity.resolve_telegram_user(message.from_user)
        await message.answer(
            "Your unified YouThopiaOS profile is active.\n"
            f"Level: {user.get('level', 1)}\n"
            f"XP: {user.get('total_xp', 0)}\n"
            f"Trust: {user.get('trust_score', 100)}"
        )

    @router.my_chat_member()
    async def track_bot_membership(event: ChatMemberUpdated, services: ServiceContainer) -> None:
        chat = await register_chat(event.chat, services, bot_name)
        if not chat:
            return

        status = event.new_chat_member.status
        if status in {"left", "kicked"}:
            await services.chats.mark_bot_status(
                bot_name,
                chat["id"],
                status,
                enabled=False,
            )

    @router.message()
    async def track_group(message: Message, services: ServiceContainer) -> None:
        await register_group_chat(message, services, bot_name)

    return router


async def run_polling_bot(
    config: BotConfig,
    services: ServiceContainer,
    *,
    description: str,
    router: Router | None = None,
) -> None:
    logger = get_logger(f"youthopia.{config.name}")
    bot = Bot(token=config.token)
    dispatcher = Dispatcher()
    dispatcher["services"] = services
    dispatcher.include_router(router or build_router(config.name, description))
    logger.info("Starting %s bot polling.", config.name)
    await dispatcher.start_polling(bot)
