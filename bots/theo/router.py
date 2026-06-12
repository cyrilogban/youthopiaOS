from __future__ import annotations

from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from core.telegram_runtime import build_router, register_group_chat
from shared.services.container import ServiceContainer


VALID_TRANSLATIONS = {"kjv", "asv", "niv", "nkjv"}
PROFILE_BUTTON = "My Profile"
TRANSLATION_BUTTON = "Translation"


def theo_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=PROFILE_BUTTON),
                KeyboardButton(text=TRANSLATION_BUTTON),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose a Theo action",
    )


def build_theo_router(description: str) -> Router:
    router = build_router("theo", description, include_base_commands=False)

    @router.message(Command("start"))
    async def start(message: Message, services: ServiceContainer) -> None:
        await register_group_chat(message, services, "theo")
        await message.answer(
            "Theo devotional bot is connected to YouThopiaOS.",
            reply_markup=theo_menu(),
        )

    @router.message(Command("help"))
    async def help_command(message: Message, services: ServiceContainer) -> None:
        await message.answer(
            "<b>Theo - Devotional Bot</b>\n"
            "\n"
            "Use the menu buttons below for now:\n"
            "\n"
            "My Profile - View your Community profile\n"
            "Translation - See how to set Bible translation\n\n"
            "To manage daily verses, use the commands /subscribe and /unsubscribe.",
            parse_mode="HTML",
            reply_markup=theo_menu(),
        )

    @router.message(F.text == PROFILE_BUTTON)
    async def menu_profile(message: Message, services: ServiceContainer) -> None:
        await send_profile(message, services)

    @router.message(Command("profile"))
    async def profile_command(message: Message, services: ServiceContainer) -> None:
        await send_profile(message, services)

    async def send_profile(message: Message, services: ServiceContainer) -> None:
        await register_group_chat(message, services, "theo")
        user = await services.identity.resolve_telegram_user(message.from_user)
        await message.answer(
            "Your Community Profile is Active\n"
            f"Level: {user.get('level', 1)}\n"
            f"XP: {user.get('total_xp', 0)}\n"
            f"Trust: {user.get('trust_score', 100)}",
            reply_markup=theo_menu(),
        )


    @router.message(F.text == TRANSLATION_BUTTON)
    async def menu_translation(message: Message) -> None:
        await message.answer(
            "Send /translation KJV, /translation ASV, /translation NIV, or /translation NKJV.",
            reply_markup=theo_menu(),
        )

    @router.message(Command("translation"))
    async def set_translation(message: Message, services: ServiceContainer) -> None:
        parts = message.text.split(maxsplit=1) if message.text else []
        if len(parts) < 2:
            await message.answer("Please specify a translation. Example: /translation KJV")
            return

        translation = parts[1].strip().lower()
        if translation not in VALID_TRANSLATIONS:
            options = ", ".join(sorted(VALID_TRANSLATIONS)).upper()
            await message.answer(f"Invalid translation. Choose from: {options}")
            return

        chat = await register_group_chat(message, services, "theo")
        if not chat:
            await message.answer("Translation setting is currently only supported in groups.")
            return

        await services.chats.set_bot_settings(
            bot_name="theo",
            chat_id=chat["id"],
            settings={"translation": translation},
        )
        await message.answer(
            f"Theo will now use {translation.upper()} for this group.",
            reply_markup=theo_menu(),
        )

    @router.message(Command("subscribe"))
    async def subscribe(message: Message, services: ServiceContainer) -> None:
        if message.chat.type == "private":
            user = await services.identity.resolve_telegram_user(message.from_user)
            
            existing_sub = await services.supabase.find_one_multi(
                "user_subscriptions",
                {"user_id": user["id"], "bot_name": "theo", "subscription_type": "daily_devotional"}
            )
            if existing_sub and existing_sub.get("enabled"):
                await message.answer(
                    "ℹ️ You are already subscribed to Theo's Bible verse of the day.",
                    reply_markup=theo_menu(),
                )
                return

            await services.users.set_subscription(
                user_id=user["id"],
                bot_name="theo",
                subscription_type="daily_devotional",
                enabled=True,
            )
            await message.answer(
                "✅ You are now subscribed to Theo's Bible verse of the day. You will receive it daily at 6:00 AM in the morning.",
                reply_markup=theo_menu(),
            )
            return

        chat = await register_group_chat(message, services, "theo")
        if not chat:
            await message.answer("Subscriptions are only supported in groups or private DMs.")
            return

        # Simple admin check for groups
        try:
            member = await message.chat.get_member(message.from_user.id)
            if member.status not in ("administrator", "creator"):
                await message.answer("❌ Only group admins can subscribe the group to daily verses.")
                return
        except Exception:
            pass

        existing_sub = await services.supabase.find_one_multi(
            "chat_subscriptions",
            {"chat_id": chat["id"], "bot_name": "theo", "subscription_type": "daily_devotional"}
        )
        if existing_sub and existing_sub.get("enabled"):
            await message.answer(
                f"ℹ️ **{message.chat.title}** is already subscribed to Theo's Bible verse of the day.",
                parse_mode="Markdown",
                reply_markup=theo_menu(),
            )
            return

        await services.chats.set_subscription(
            bot_name="theo",
            chat_id=chat["id"],
            subscription_type="daily_devotional",
            enabled=True,
        )
        await message.answer(
            f"✅ **{message.chat.title}** is now subscribed to Theo's Bible verse of the day. You will receive it daily at 6:00 AM in the morning.",
            parse_mode="Markdown",
            reply_markup=theo_menu(),
        )

    @router.message(Command("unsubscribe"))
    async def unsubscribe(message: Message, services: ServiceContainer) -> None:
        if message.chat.type == "private":
            user = await services.identity.resolve_telegram_user(message.from_user)
            
            existing_sub = await services.supabase.find_one_multi(
                "user_subscriptions",
                {"user_id": user["id"], "bot_name": "theo", "subscription_type": "daily_devotional"}
            )
            if not existing_sub or not existing_sub.get("enabled"):
                await message.answer(
                    "ℹ️ You are not currently subscribed to Theo's Bible verse of the day.",
                    reply_markup=theo_menu(),
                )
                return

            await services.users.set_subscription(
                user_id=user["id"],
                bot_name="theo",
                subscription_type="daily_devotional",
                enabled=False,
            )
            await message.answer(
                "🚫 You have unsubscribed from Theo's Bible verse of the day.",
                reply_markup=theo_menu(),
            )
            return

        chat = await register_group_chat(message, services, "theo")
        if not chat:
            await message.answer("Unsubscriptions are only supported in groups or private DMs.")
            return

        # Simple admin check for groups
        try:
            member = await message.chat.get_member(message.from_user.id)
            if member.status not in ("administrator", "creator"):
                await message.answer("❌ Only group admins can unsubscribe the group from daily verses.")
                return
        except Exception:
            pass

        existing_sub = await services.supabase.find_one_multi(
            "chat_subscriptions",
            {"chat_id": chat["id"], "bot_name": "theo", "subscription_type": "daily_devotional"}
        )
        if not existing_sub or not existing_sub.get("enabled"):
            await message.answer(
                f"ℹ️ **{message.chat.title}** is not currently subscribed to Theo's Bible verse of the day.",
                parse_mode="Markdown",
                reply_markup=theo_menu(),
            )
            return

        await services.chats.set_subscription(
            bot_name="theo",
            chat_id=chat["id"],
            subscription_type="daily_devotional",
            enabled=False,
        )
        await message.answer(
            f"🚫 **{message.chat.title}** has been unsubscribed from Theo's Bible verse of the day.",
            parse_mode="Markdown",
            reply_markup=theo_menu(),
        )

    @router.startup()
    async def on_startup(bot: Bot, services: ServiceContainer) -> None:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from bots.theo.services.delivery_service import DeliveryService
        from zoneinfo import ZoneInfo
        import logging

        logger = logging.getLogger(__name__)
        delivery_service = DeliveryService(bot=bot, services=services)
        
        # Schedule the broadcast every day at 6:00 AM
        scheduler = AsyncIOScheduler(timezone=ZoneInfo("Africa/Lagos"))
        scheduler.add_job(delivery_service.broadcast_votd, 'cron', hour=6, minute=0)
        scheduler.start()
        logger.info("VOTD Scheduler started. Next run at 6:00 AM.")

    @router.message(Command("broadcast_votd"))
    async def manual_broadcast_votd(message: Message, services: ServiceContainer) -> None:
        from bots.theo.services.delivery_service import DeliveryService
        
        await message.answer("Starting manual VOTD broadcast to all subscribers...")
        delivery_service = DeliveryService(bot=message.bot, services=services)
        
        result = await delivery_service.broadcast_votd()
        
        summary = (
            f"✅ **Broadcast Completed!**\n\n"
            f"**Status:** {result.get('status')}\n"
            f"**Reference:** {result.get('reference', 'N/A')}\n"
            f"**Successfully Sent:** {result.get('success_count', 0)}\n"
            f"**Failed:** {result.get('failure_count', 0)}"
        )
        await message.answer(summary, parse_mode="Markdown")

    return router
