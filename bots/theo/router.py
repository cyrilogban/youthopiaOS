from __future__ import annotations

import random

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

FOOTER_SCRIPTURES = [
    "Let your light shine before others. — Matthew 5:16",
    "I can do all things through Christ who strengthens me. — Philippians 4:13",
    "For God has not given us a spirit of fear, but of power. — 2 Timothy 1:7",
    "Be strong and courageous. Do not be afraid. — Joshua 1:9",
    "The Lord is my shepherd; I shall not want. — Psalm 23:1",
    "Trust in the Lord with all your heart. — Proverbs 3:5",
]

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
            "Hi there, I'm Theo. 🤍\n\n"
            "I serve <b>YOUTHOPIA BIBLE COMMUNITY</b> as your dedicated Bible companion bot. "
            "Every YouTopian in this community has me in their corner, keeping Scripture alive in their daily journey.\n\n"
            "Think of me as the community's digital anchor to God's Word.\n\n"
            "<b>What I bring to you:</b>\n"
            "🌅 Daily Verse every morning at 6 AM when you subscribe to daily verses\n"
            "📖 Instant Scripture lookup on demand in the chat e.g John 3:16\n"
            "👤 Community profile to track your growth\n\n"
            "Welcome to the family, YouTopian. Use the buttons below to get started. 💜\n\n"
            "<b>Join our communities:</b>\n"
            "📱 Telegram Community\n"
            "💬 WhatsApp Community\n\n"
            "<i>Sharing God's Love All The Way.</i>"
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
        subscribed = "Subscribed" if (sub and sub.get("enabled")) else "Not subscribed"

        # Check translation preference
        state_row = await services.supabase.find_one_multi(
            "bot_user_state",
            {"bot_name": "theo", "user_id": user["id"]}
        )
        state = (state_row.get("state", {}) or {}) if state_row else {}
        translation = state.get("translation", "KJV").upper()

        verse_text = random.choice(FOOTER_SCRIPTURES)

        await message.answer(
            "✝️  YouThopia Profile\n\n"
            "Beloved Child of God,\n"
            "you are doing well in your walk.\n\n"
            f"📖 Name: {name}\n"
            f"⛰ Level: {user.get('level', 1)}  |  XP: {user.get('total_xp', 0)}\n"
            f"🕊 Trust: {user.get('trust_score', 100)}\n"
            f"🔤 {translation}\n"
            f"🌅 Daily Verse: {subscribed}\n\n"
            f"\"{verse_text}\"",
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
                THEO_PHOTO = photos.photos[0][-1].file_id
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
