from __future__ import annotations

import calendar
import random
from datetime import date, datetime

from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from core.telegram_runtime import build_router, register_group_chat
from shared.services.container import ServiceContainer
from bots.theo.handlers.messages import handle_bible_detection


VALID_TRANSLATIONS = {"kjv", "asv", "web", "bbe"}
PROFILE_BUTTON = "My Profile"
TRANSLATION_BUTTON = "Translation"

THEO_PHOTO: str | None = None


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Telegram", url="https://t.me/youthopiabiblecommunity"),
            InlineKeyboardButton(text="WhatsApp", url="https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn"),
        ],
        [
            InlineKeyboardButton(text="My Profile", callback_data="profile"),
            InlineKeyboardButton(text="Translation", callback_data="translation"),
        ],
    ])


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
        
        welcome_text = (
            "I'm Theo.\n\n"
            "The Bible bot that lives inside\n"
            "<b>YOUTHOPIA BIBLE COMMUNITY</b>.\n\n"
            "My job is simple: keep every YouTopian\n"
            "connected to God's Word, every single day.\n\n"
            "6 AM verse, daily\n"
            "Any Scripture on demand\n"
            "Your YouTopian profile and growth stats\n\n"
            "Set up your experience below and let's go.\n\n"
            "Sharing God's Love All The Way."
        )
        
        if THEO_PHOTO:
            await message.answer_photo(
                photo=THEO_PHOTO,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=welcome_keyboard(),
            )
        else:
            await message.answer(
                welcome_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=welcome_keyboard(),
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

    @router.callback_query(F.data == "profile")
    async def inline_profile(callback: CallbackQuery, services: ServiceContainer) -> None:
        await callback.answer()
        await send_profile(callback.message, services)

    @router.callback_query(F.data == "translation")
    async def inline_translation(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            "Send /translation KJV, /translation ASV, /translation WEB, or /translation BBE.",
        )

    async def send_profile(message: Message, services: ServiceContainer) -> None:
        await register_group_chat(message, services, "theo")
        user = await services.identity.resolve_telegram_user(message.from_user)
        name = message.from_user.first_name or user.get("display_name", "Beloved")

        # Check daily devotional subscription
        sub = await services.supabase.find_one_multi(
            "user_subscriptions",
            {"user_id": user["id"], "bot_name": "theo", "subscription_type": "daily_devotional"}
        )
        subscribed_text = "Subscribed" if (sub and sub.get("enabled")) else "Not subscribed"

        # Check translation preference
        state_row = await services.supabase.find_one_multi(
            "bot_user_state",
            {"bot_name": "theo", "user_id": user["id"]}
        )
        state = (state_row.get("state", {}) or {}) if state_row else {}
        translation = state.get("translation", "KJV").upper()

        # Format join date from users.created_at
        created = user.get("created_at")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                join_date = f"{calendar.month_abbr[dt.month]} {dt.year}"
            except Exception:
                join_date = "Unknown"
        else:
            join_date = "Unknown"

        # Get last_seen_at from telegram_accounts
        account = await services.supabase.find_one("telegram_accounts", "telegram_id", message.from_user.id)
        if account and account.get("last_seen_at"):
            try:
                last_dt = datetime.fromisoformat(account["last_seen_at"].replace("Z", "+00:00"))
                if last_dt.date() == date.today():
                    last_seen_text = "Today"
                else:
                    last_seen_text = f"{calendar.month_abbr[last_dt.month]} {last_dt.day}"
            except Exception:
                last_seen_text = "Today"
        else:
            last_seen_text = "Today"

        level = user.get("level", 1)
        xp = user.get("total_xp", 0)
        trust = user.get("trust_score", 100)

        await message.answer(
            "✝ YOUTHOPIA  BIBLE  COMMUNITY PROFILE\n\n"
            "<blockquote>"
            f"{name}  ·  Member since {join_date}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Level {level}           {xp} XP\n"
            f"  Trust Score {trust}    Bible: {translation}\n"
            f"  Daily Verse: {subscribed_text}\n"
            "</blockquote>\n\n"
            f"  Last seen: {last_seen_text}",
            parse_mode="HTML",
            reply_markup=theo_menu(),
        )


    @router.message(F.text == TRANSLATION_BUTTON)
    async def menu_translation(message: Message) -> None:
        await message.answer(
            "Send /translation KJV, /translation ASV, /translation WEB, or /translation BBE.",
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
        if chat:
            # Group Chat
            await services.chats.set_bot_settings(
                bot_name="theo",
                chat_id=chat["id"],
                settings={"translation": translation},
            )
            await message.answer(
                f"Theo will now use {translation.upper()} for this group.",
                reply_markup=theo_menu(),
            )
        else:
            # Private DM
            user = await services.identity.resolve_telegram_user(message.from_user)
            
            existing_state = await services.supabase.find_one_multi(
                "bot_user_state",
                {"bot_name": "theo", "user_id": user["id"]}
            )
            state = existing_state.get("state", {}) if existing_state else {}
            state["translation"] = translation
            
            await services.supabase.upsert(
                "bot_user_state",
                {
                    "bot_name": "theo",
                    "user_id": user["id"],
                    "state": state
                },
                on_conflict="user_id,bot_name"
            )
            await message.answer(
                f"Theo will now use {translation.upper()} for your personal messages.",
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

    # ------------------------------------------------------------------
    # Bible reference auto-detection (catches remaining text messages)
    # ------------------------------------------------------------------
    @router.message(F.text)
    async def bible_detection(message: Message, services: ServiceContainer) -> None:
        await handle_bible_detection(message, services)

    @router.startup()
    async def on_startup(bot: Bot, services: ServiceContainer) -> None:
        global THEO_PHOTO

        # Fetch bot profile photo
        try:
            photos = await bot.get_user_profile_photos(bot.id)
            if photos and photos.photos:
                sizes = photos.photos[0]
                THEO_PHOTO = sizes[len(sizes) // 3].file_id if len(sizes) >= 2 else sizes[0].file_id
        except Exception:
            pass

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


    return router
