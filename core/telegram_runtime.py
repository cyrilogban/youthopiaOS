from __future__ import annotations

import os
import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import (
    BotCommand,
    Chat,
    ChatMemberUpdated,
    Message,
    TelegramObject,
    InlineKeyboardMarkup,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeChat,
)

from core.config import BotConfig
from core.admin_commands import create_admin_router
from shared.logging.logger import get_logger
from shared.services.container import ServiceContainer
from shared.utils.ui import get_open_app_inline_button


async def delayed_delete_message(bot: Bot, chat_id: int, message_id: int, delay_seconds: int = 0) -> None:
    """Safely deletes a message after a non-blocking delay."""
    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


class SmartGroupCommandCleanerMiddleware(BaseMiddleware):
    """Middleware that automatically manages group command & button trigger message lifecycle:
    - Moderation & Governance commands (/warn, /mute, /ban, /setrank, /biblestudy, etc.):
      Retained for 3 minutes (180s) so the community sees the disciplinary action,
      then cleanly deleted in the background.
    - Navigation, Menus, Queries, & Bottom Reply Button clicks (/start, /profile, 🏆 Rankings, etc.):
      Deleted immediately (0s) to keep group chat history clean.
    - Private DMs: Untouched (0 deletion) so user command history is preserved.
    """

    MODERATION_GOVERNANCE_COMMANDS: set[str] = {
        "warn", "mute", "unmute", "ban", "unban", "kick",
        "lock", "unlock", "biblestudy", "endbiblestudy", "appeal",
        "setrank", "stats", "botstats", "groups", "admin",
        "new_event", "send_votd", "setup_gateway", "autoquiz_on", "autoquiz_off",
    }

    # Standard persistent reply keyboard button labels across all 5 bots
    REPLY_KEYBOARD_TRIGGERS: set[str] = {
        "👤 My Profile", "Open App", "ℹ️ Help", "🌐 Community",
        "🔍 Search Scripture", "🔖 Saved Verses", "🌐 Translation",
        "🎯 Play Quizzes", "🏆 Leaderboard", "🏆 Rankings", "⭐ My Points", "🛑 Quit Quiz",
        "📅 View Calendar", "📅 Calendar", "🎫 My Events", "🎂 Add Birthday", "🔔 Reminders",
        "📝 Submit Appeal", "📝 Appeal",
    }

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.chat.type in ("group", "supergroup") and event.text:
            text = event.text.strip()
            bot: Bot | None = data.get("bot") or getattr(event, "bot", None)

            if bot:
                if text.startswith("/"):
                    cmd = self._extract_command(text)
                    if cmd:
                        delay = 180 if cmd in self.MODERATION_GOVERNANCE_COMMANDS else 0
                        asyncio.create_task(
                            delayed_delete_message(bot, event.chat.id, event.message_id, delay_seconds=delay)
                        )
                elif text in self.REPLY_KEYBOARD_TRIGGERS:
                    # Reply keyboard button tap in group: delete immediately (0s)
                    asyncio.create_task(
                        delayed_delete_message(bot, event.chat.id, event.message_id, delay_seconds=0)
                    )

        return await handler(event, data)

    @staticmethod
    def _extract_command(text: str) -> str | None:
        if not text.startswith("/"):
            return None
        token = text.split()[0][1:]
        return token.split("@")[0].lower() if token else None


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

    try:
        chat = await services.chats.upsert_chat(
            chat_obj.id,
            chat_obj.type,
            title=chat_obj.title,
            username=chat_obj.username,
        )
        if bot_name and chat and "id" in chat:
            try:
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
                    existing_sub = await services.chats.get_subscription("theo", chat["id"], "daily_devotional")
                    if not existing_sub:
                        await services.chats.set_subscription(
                            bot_name="theo",
                            chat_id=chat["id"],
                            subscription_type="daily_devotional",
                            enabled=True,
                        )
            except Exception as e:
                logger.warning(f"Error updating bot settings in register_chat for {bot_name}: {e}")
        return chat
    except Exception as e:
        logger.warning(f"Failed to upsert chat in register_chat for {bot_name}: {e}")
        return None


async def register_group_chat(
    message: Message,
    services: ServiceContainer,
    bot_name: str,
) -> dict | None:
    return await register_chat(message.chat, services, bot_name)


def build_router(bot_name: str, description: str, *, include_base_commands: bool = True) -> Router:
    router = Router(name=bot_name)
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

        @router.message(Command("app", "miniapp"))
        async def handle_app_command(message: Message) -> None:
            markup = InlineKeyboardMarkup(inline_keyboard=[[get_open_app_inline_button()]])
            await message.answer(
                "Open <b>YOUTHOPIA BIBLE COMMUNITY</b> Mini App:\n"
                "<i>Sharing God's Love All The Way</i>",
                parse_mode="HTML",
                reply_markup=markup
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
    dispatcher.message.outer_middleware(SmartGroupCommandCleanerMiddleware())
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
        allowed_updates=[
            "message",
            "edited_message",
            "channel_post",
            "edited_channel_post",
            "callback_query",
            "poll",
            "poll_answer",
            "my_chat_member",
            "chat_member",
            "chat_join_request",
        ]
    )
