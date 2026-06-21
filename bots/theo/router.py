from __future__ import annotations

import calendar
import random
from datetime import date, datetime
from typing import Any

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
SAVED_VERSES_BUTTON = "My Saved Verses"

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
                KeyboardButton(text=SAVED_VERSES_BUTTON),
            ],
            [
                KeyboardButton(text=TRANSLATION_BUTTON),
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose a Theo action",
    )


def build_theo_router(description: str) -> Router:
    router = build_router("theo", description, include_base_commands=False)

    @router.message(Command("start"))
    async def start(message: Message, services: ServiceContainer) -> None:
        await register_group_chat(message, services, "theo")
        
        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"
        
        if user.get("engagement_level") == "new":
            welcome_text = (
                f"<blockquote>Hi there, I'm Theo. 🤍\n\n"
                f"I serve YOUTHOPIA BIBLE COMMUNITY as your\n"
                f"dedicated Bible companion bot. Every YouTopian\n"
                f"in this community has me in their corner,\n"
                f"keeping Scripture alive in their daily journey.\n\n"
                f"Think of me as the community's digital\n"
                f"anchor to God's Word.\n\n"
                f"What I bring to you:\n"
                f"🌅 Daily Verse every morning at 6 AM when you subscribe to daily verses\n"
                f"📖 Instant Scripture lookup on demand in the chat e.g John 3:16\n"
                f"👤 Community profile to track your growth\n\n"
                f"Welcome to the family, {first_name}.\n"
                f"Use the menu below to get started. 💜\n\n"
                f"Sharing God's Love All The Way.\n"
                f"#YouThopia #YouThopiaBibleCommunity</blockquote>"
            )
            await services.users.set_engagement_level(user["id"], "active")
        else:
            welcome_text = (
                f"<blockquote>Welcome back, {first_name}! 💜\n\n"
                f"I'm Theo, your scripture companion built for the YOUTHOPIA Bible Community.\n\n"
                f"Use the menu below to check your profile, change your translation, or look up verses!</blockquote>"
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
        first_name = message.from_user.first_name or "Friend"
        help_text = (
            f"<b>Welcome to YOUTHOPIA BIBLE COMMUNITY, {first_name}!</b>\n\n"
            "We are a Cross platform Gen Z Christian community where faith meets real life. We grow together, share God's Word, and support one another on the journey of becoming who God created us to be.\n\n"
            "Sharing God's Love All The Way\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "You're currently talking to <b>Theo</b>\n"
            "Theo is the devotional heart of the YouThopia bot family. He sends you daily Bible verses, helps you reflect on Scripture, and keeps you grounded in the Word every single day.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>Meet the YouThopia Bot Family</b>\n\n"
            "Every bot in our community has a unique role. Here is who is here for you:\n\n"
            "<b>Theo</b> - <a href=\"https://t.me/iamtheobot\">@iamtheobot</a>\n"
            "Your daily Bible companion. Devotionals, verses, and spiritual reflection.\n\n"
            "<b>Lusy</b> - <a href=\"https://t.me/iamlusybot\">@iamlusybot</a>\n"
            "Games, XP, and fun! Earn points and grow your YouTopian rank.\n\n"
            "<b>Pete</b> - <a href=\"https://t.me/iampetebot\">@iampetebot</a>\n"
            "Security and moderation. Keeping our community safe and in order.\n\n"
            "<b>Ed</b> - <a href=\"https://t.me/iamedyybot\">@iamedyybot</a>\n"
            "Events and announcements. Never miss what is happening in YouThopia.\n\n"
            "<b>Susy</b> - <a href=\"https://t.me/iamsusiebot\">@iamsusiebot</a>\n"
            "Your first friend here. Welcomes new YouTopians and gets you settled in.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>How to Use Theo</b>\n\n"
            "Use the menu buttons below to get started:\n"
            "- My Profile: View your YouThopia community profile\n"
            "- Translation: Set your preferred Bible translation\n\n"
            "To manage your daily verse delivery:\n"
            "/subscribe - Start receiving daily Bible verses\n"
            "/unsubscribe - Pause your daily verses"
        )
        await message.answer(
            help_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=theo_menu(),
        )

    @router.message(F.text == PROFILE_BUTTON)
    async def menu_profile(message: Message, services: ServiceContainer) -> None:
        await send_profile(message, services)

    @router.message(Command("profile"))
    async def profile_command(message: Message, services: ServiceContainer) -> None:
        await send_profile(message, services)
        
    @router.message(F.text == SAVED_VERSES_BUTTON)
    async def menu_saved_verses(message: Message, services: ServiceContainer) -> None:
        await send_saved_verses_page(message, services, page=1)

    from bots.theo.utils.keyboards import SavedVersesPage
    
    @router.callback_query(SavedVersesPage.filter())
    async def inline_saved_verses_page(callback: CallbackQuery, callback_data: SavedVersesPage, services: ServiceContainer) -> None:
        await callback.answer()
        await send_saved_verses_page(callback, services, page=callback_data.page)
        
    @router.callback_query(F.data == "ignore")
    async def inline_ignore(callback: CallbackQuery) -> None:
        await callback.answer()

    @router.callback_query(F.data == "profile")
    async def inline_profile(callback: CallbackQuery, services: ServiceContainer) -> None:
        await callback.answer()
        await send_profile(callback.message, services, telegram_user=callback.from_user)

    @router.callback_query(F.data == "translation")
    async def inline_translation(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            "Send /translation KJV, /translation ASV, /translation WEB, or /translation BBE.",
        )

    from bots.theo.utils.keyboards import VerseAction

    @router.callback_query(VerseAction.filter(F.action == "save"))
    async def handle_save_verse(callback: CallbackQuery, callback_data: VerseAction, services: ServiceContainer):
        user = await services.identity.resolve_telegram_user(callback.from_user)
        # Re-add space to reference
        reference = callback_data.reference.replace("_", " ")
        saved = await services.users.save_verse(
            user_id=user["id"], 
            bot_name="theo", 
            reference=reference, 
            category=callback_data.category
        )
        if saved:
            await callback.answer("Verse saved successfully.", show_alert=True)
        else:
            await callback.answer("This verse is already in your saved verses.", show_alert=True)

    @router.callback_query(VerseAction.filter(F.action == "next"))
    async def handle_next_verse(callback: CallbackQuery, callback_data: VerseAction, services: ServiceContainer):
        import random
        from bots.theo.services.devotional_service import VOTDService
        from bots.theo.utils.keyboards import build_verse_actions_keyboard
        from bots.theo.utils.seed_votd import CURATED_REFERENCES
        
        votd_service = VOTDService(services.supabase)
        
        # Get translation preference
        translation = "kjv"
        user = await services.identity.resolve_telegram_user(callback.from_user)
        user_state = await services.supabase.find_one_multi(
            "bot_user_state",
            {"bot_name": "theo", "user_id": user["id"]}
        )
        if user_state and "state" in user_state:
            translation = user_state["state"].get("translation", "kjv")
        
        # Pick a random curated verse, avoiding the current one
        current_ref = callback_data.reference.replace("_", " ")
        choices = [r for r in CURATED_REFERENCES if r != current_ref]
        new_ref = random.choice(choices) if choices else current_ref
        
        text = await votd_service.fetch_bible_text(new_ref, translation)
        
        if text:
            header = f"<b>{new_ref} ({translation.upper()})</b>"
            blockquote = f"<blockquote>{text}</blockquote>"
            reply_text = f"{header}\n{blockquote}"
            
            markup = build_verse_actions_keyboard(category=callback_data.category, reference=new_ref)
            await callback.message.edit_text(reply_text, parse_mode="HTML", reply_markup=markup)
            await callback.answer()
        else:
            await callback.answer("Failed to fetch text.", show_alert=True)

    async def send_profile(message: Message, services: ServiceContainer, telegram_user: Any | None = None) -> None:
        await register_group_chat(message, services, "theo")
        user_from = telegram_user or message.from_user
        user = await services.identity.resolve_telegram_user(user_from)
        name = user_from.first_name or user.get("display_name", "Beloved")

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
        account = await services.supabase.find_one("telegram_accounts", "telegram_id", user_from.id)
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

    async def send_saved_verses_page(
        message: Message | CallbackQuery, 
        services: ServiceContainer, 
        page: int = 1
    ) -> None:
        import asyncio
        from bots.theo.services.devotional_service import VOTDService
        
        telegram_user = message.from_user
        user = await services.identity.resolve_telegram_user(telegram_user)
        
        translation = "kjv"
        user_state = await services.supabase.find_one_multi(
            "bot_user_state",
            {"bot_name": "theo", "user_id": user["id"]}
        )
        if user_state and "state" in user_state:
            translation = user_state["state"].get("translation", "kjv")
            
        verses = await services.users.get_saved_verses(user["id"], "theo")
        
        is_callback = isinstance(message, CallbackQuery)
        reply_target = message.message if is_callback else message
        
        if not verses:
            msg = "You have no saved verses yet.\n\nTap <b>Save</b> on any verse to save it here."
            if is_callback:
                await reply_target.edit_text(msg, parse_mode="HTML")
            else:
                await reply_target.answer(msg, parse_mode="HTML")
            return
            
        PER_PAGE = 3
        total_pages = max(1, (len(verses) + PER_PAGE - 1) // PER_PAGE)
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * PER_PAGE
        page_verses = verses[start_idx : start_idx + PER_PAGE]
        
        votd_service = VOTDService(services.supabase)
        
        tasks = [
            votd_service.fetch_bible_text(v["reference"], translation) 
            for v in page_verses
        ]
        fetched_texts = await asyncio.gather(*tasks, return_exceptions=True)
        
        parts = [f"<b>My Saved Verses</b> (Page {page} of {total_pages})"]
        
        for v, text in zip(page_verses, fetched_texts):
            ref = v["reference"]
            if isinstance(text, Exception) or not text:
                text = "Could not fetch verse text."
                
            parts.append(f"<b>{ref}</b> ({translation.upper()})")
            
            if len(text) > 150:
                parts.append(f"<blockquote expandable>{text}</blockquote>")
            else:
                parts.append(f"<blockquote>{text}</blockquote>")
                
        reply_text = "\n\n".join(parts)
        
        inline_kb = []
        nav_row = []
        if page > 1:
            from bots.theo.utils.keyboards import SavedVersesPage
            nav_row.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=SavedVersesPage(page=page-1).pack()))
        
        nav_row.append(InlineKeyboardButton(text=f"• {page} / {total_pages} •", callback_data="ignore"))
            
        if page < total_pages:
            from bots.theo.utils.keyboards import SavedVersesPage
            nav_row.append(InlineKeyboardButton(text="Next ➡️", callback_data=SavedVersesPage(page=page+1).pack()))
            
        inline_kb.append(nav_row)
        markup = InlineKeyboardMarkup(inline_keyboard=inline_kb)
        
        if is_callback:
            await reply_target.edit_text(reply_text, parse_mode="HTML", reply_markup=markup)
        else:
            await reply_target.answer(reply_text, parse_mode="HTML", reply_markup=markup)

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

    # ------------------------------------------------------------------
    # Inline Query Handler (for the Share button)
    # ------------------------------------------------------------------
    from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
    import asyncio

    @router.inline_query()
    async def inline_query_handler(inline_query: InlineQuery, services: ServiceContainer) -> None:
        query = inline_query.query.strip()
        if not query:
            return

        from bots.theo.utils.bible_ref_parser import find_scripture_references
        refs = find_scripture_references(query)
        
        if not refs:
            return
            
        # Get user's preferred translation
        translation = "kjv"
        user = await services.identity.resolve_telegram_user(inline_query.from_user)
        user_state = await services.supabase.find_one_multi(
            "bot_user_state",
            {"bot_name": "theo", "user_id": user["id"]}
        )
        if user_state and "state" in user_state:
            translation = user_state["state"].get("translation", "kjv")

        from bots.theo.services.devotional_service import VOTDService
        votd_service = VOTDService(services.supabase)
        
        results = []
        for ref in refs:
            try:
                # 3-second timeout protection per fetch so the inline menu doesn't hang
                text = await asyncio.wait_for(
                    votd_service.fetch_bible_text(ref.reference, translation),
                    timeout=3.0
                )
                if text:
                    header = f"<b>{ref.reference} ({translation.upper()})</b>"
                    blockquote = f"<blockquote>{text}</blockquote>"
                    full_message = f"{header}\n{blockquote}"
                    
                    result = InlineQueryResultArticle(
                        id=f"ref_{ref.reference.replace(' ', '_').replace(':', '')}",
                        title=f"{ref.reference} ({translation.upper()})",
                        description=(text[:100] + "...") if len(text) > 100 else text,
                        input_message_content=InputTextMessageContent(
                            message_text=full_message,
                            parse_mode="HTML"
                        )
                    )
                    results.append(result)
            except asyncio.TimeoutError:
                continue
                
        if results:
            await inline_query.answer(results, cache_time=3600)

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
