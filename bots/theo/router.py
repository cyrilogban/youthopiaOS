from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from core.telegram_runtime import build_router, register_group_chat
from shared.services.container import ServiceContainer
from shared.utils.ui import (
    BOT_FAMILY_DIRECTORY_TEXT,
    get_community_links_keyboard,
    render_shared_profile_card,
)
from bots.theo.handlers.messages import handle_bible_detection
from bots.theo.services.devotional_service import VOTDService
from bots.theo.utils.keyboards import (
    SavedVersesPage,
    VerseAction,
    build_theo_reply_keyboard,
    build_theo_welcome_inline_keyboard,
    build_verse_actions_keyboard,
)

logger = logging.getLogger(__name__)

VALID_TRANSLATIONS = {"kjv", "asv", "web", "bbe"}
THEO_PHOTO: str | None = None


def build_translation_selection_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for selecting Bible translation preference."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="KJV (King James)", callback_data="theo_set_trans_kjv"),
                InlineKeyboardButton(text="ASV (American Standard)", callback_data="theo_set_trans_asv"),
            ],
            [
                InlineKeyboardButton(text="WEB (World English)", callback_data="theo_set_trans_web"),
                InlineKeyboardButton(text="BBE (Basic English)", callback_data="theo_set_trans_bbe"),
            ]
        ]
    )


def build_theo_router(description: str) -> Router:
    router = build_router("theo", description, include_base_commands=False)

    # -------------------------------------------------------------------------
    # COMMAND: /start
    # -------------------------------------------------------------------------
    @router.message(Command("start"))
    async def start(message: Message, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return

        await register_group_chat(message, services, "theo")
        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"

        if user.get("engagement_level") == "new":
            welcome_text = (
                f"<blockquote>Hi there, I'm Theo. 🤍\n\n"
                f"I serve YOUTHOPIA BIBLE COMMUNITY as your dedicated Bible companion bot. "
                f"Every YouTopian in this community has me in their corner, keeping Scripture alive in their daily journey.\n\n"
                f"Think of me as the community's digital anchor to God's Word.\n\n"
                f"What I bring to you:\n"
                f"🌅 Daily Verse every morning at 6 AM when you subscribe\n"
                f"📖 Instant Scripture lookup on demand in chat (e.g. John 3:16)\n"
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
                f"I'm Theo, your scripture companion built for YOUTHOPIA BIBLE COMMUNITY.\n\n"
                f"Use the menu buttons below to check your profile, search scripture, or bookmark verses!</blockquote>"
            )

        reply_menu = build_theo_reply_keyboard()
        inline_menu = build_theo_welcome_inline_keyboard()

        if THEO_PHOTO:
            await message.answer_photo(
                photo=THEO_PHOTO,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=inline_menu,
            )
        else:
            await message.answer(
                welcome_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=inline_menu,
            )
            
        # Send persistent reply keyboard menu
        await message.answer(
            "Navigation Menu Loaded 👇",
            reply_markup=reply_menu
        )

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 1: 👤 My Profile / /profile
    # -------------------------------------------------------------------------
    @router.message(F.text == "👤 My Profile")
    @router.message(Command("profile"))
    async def profile_handler(message: Message, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return
        await send_theo_profile(message, services)

    @router.callback_query(F.data == "theo_profile")
    async def inline_profile_handler(callback: CallbackQuery, services: ServiceContainer) -> None:
        await callback.answer()
        await send_theo_profile(callback.message, services, telegram_user=callback.from_user)

    async def send_theo_profile(
        message: Message, services: ServiceContainer, telegram_user: Any | None = None
    ) -> None:
        await register_group_chat(message, services, "theo")
        user_from = telegram_user or message.from_user
        user = await services.identity.resolve_telegram_user(user_from)

        # Fetch daily devotional subscription status
        sub = await services.users.get_subscription(user["id"], "theo", "daily_devotional")
        subscribed_text = "Subscribed (6:00 AM)" if (sub and sub.get("enabled")) else "Not subscribed"

        # Fetch translation preference
        state = await services.users.get_user_state(user["id"], "theo")
        translation = state.get("translation", "kjv").upper()

        # Theo-specific stats for profile card
        bot_stats = [
            f"📖 Translation: <b>{translation}</b>",
            f"🌅 Daily Verse: <b>{subscribed_text}</b>",
        ]

        card_text = render_shared_profile_card(
            user_data=user,
            telegram_first_name=user_from.first_name or "Friend",
            bot_specific_stats=bot_stats
        )

        await message.answer(
            card_text,
            parse_mode="HTML",
            reply_markup=build_theo_reply_keyboard(),
        )

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 2: ℹ️ Help / /help
    # -------------------------------------------------------------------------
    @router.message(F.text == "ℹ️ Help")
    @router.message(Command("help"))
    async def help_handler(message: Message) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return
        await send_theo_help(message)

    @router.callback_query(F.data == "theo_help")
    async def inline_help_handler(callback: CallbackQuery) -> None:
        await callback.answer()
        await send_theo_help(callback.message)

    async def send_theo_help(message: Message) -> None:
        help_text = (
            "<b>📖 Theo | Daily Word Help Guide</b>\n"
            "<blockquote>I am Theo (@iamtheobot), your devotional companion in YOUTHOPIA BIBLE COMMUNITY.\n\n"
            "<b>Theo Features & Commands</b>\n"
            "• 📖 <b>Daily Verse:</b> Get today's verse on demand.\n"
            "• 🔍 <b>Search Scripture:</b> Type any reference in chat (e.g. John 3:16).\n"
            "• 🔖 <b>Saved Verses:</b> View your saved bookmarks.\n"
            "• 🌐 <b>Translation:</b> Switch between KJV, ASV, WEB, and BBE.\n"
            "• <b>/subscribe:</b> Receive Daily Verses every morning at 6:00 AM.\n"
            "• <b>/unsubscribe:</b> Pause daily verse notifications.</blockquote>\n\n"
            f"{BOT_FAMILY_DIRECTORY_TEXT}\n\n"
            "Sharing God's Love All The Way 💜"
        )
        await message.answer(
            help_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=get_community_links_keyboard(),
        )

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 3: 🌐 Community Links
    # -------------------------------------------------------------------------
    @router.message(F.text == "🌐 Community Links")
    async def community_links_handler(message: Message) -> None:
        if message.chat.type != "private":
            return
        await message.answer(
            "<b>🌐 YOUTHOPIA BIBLE COMMUNITY LINKS</b>\n"
            "<blockquote>Connect with us across all platforms to stay updated, fellowship, and grow together! 💜</blockquote>",
            parse_mode="HTML",
            reply_markup=get_community_links_keyboard()
        )

    @router.callback_query(F.data == "theo_community_links")
    async def inline_community_links_handler(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            "<b>🌐 YOUTHOPIA BIBLE COMMUNITY LINKS</b>\n"
            "<blockquote>Connect with us across all platforms to stay updated, fellowship, and grow together! 💜</blockquote>",
            parse_mode="HTML",
            reply_markup=get_community_links_keyboard()
        )

    @router.callback_query(F.data == "global_ignore")
    async def inline_global_ignore(callback: CallbackQuery) -> None:
        await callback.answer("Threads community link coming soon!", show_alert=True)

    # -------------------------------------------------------------------------
    # BOT-SPECIFIC BUTTON 1: 📖 Daily Verse
    # -------------------------------------------------------------------------
    @router.message(F.text == "📖 Daily Verse")
    @router.callback_query(F.data == "theo_daily_verse")
    async def daily_verse_handler(event: Message | CallbackQuery, services: ServiceContainer) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event

        if is_callback:
            await event.answer()

        user = await services.identity.resolve_telegram_user(event.from_user)
        user_state = await services.users.get_user_state(user["id"], "theo")
        translation = user_state.get("translation", "kjv") if user_state else "kjv"

        votd_service = VOTDService(services.supabase)
        votd_data = await votd_service.get_today_votd(translation=translation)

        if votd_data:
            ref = votd_data["reference"]
            text = votd_data["text"]
            reflection = votd_data.get("reflection", "")

            reply_text = (
                f"<b>📖 Daily Verse of the Day</b>\n\n"
                f"<b>{ref} ({translation.upper()})</b>\n"
                f"<blockquote>{text}</blockquote>"
            )
            if reflection:
                reply_text += f"\n\n💭 <b>Reflection:</b>\n<i>{reflection}</i>"

            markup = build_verse_actions_keyboard(category="votd", reference=ref)
            await message.answer(reply_text, parse_mode="HTML", reply_markup=markup)
        else:
            await message.answer("⚠️ Unable to fetch today's Daily Verse. Please try again in a moment.")

    # -------------------------------------------------------------------------
    # BOT-SPECIFIC BUTTON 2: 🔍 Search Scripture
    # -------------------------------------------------------------------------
    @router.message(F.text == "🔍 Search Scripture")
    async def search_scripture_handler(message: Message) -> None:
        if message.chat.type != "private":
            return
        prompt_text = (
            "<b>🔍 Search Scripture</b>\n\n"
            "Type any Bible reference directly in this chat! Examples:\n"
            "• <code>John 3:16</code>\n"
            "• <code>Psalm 23:1-6</code>\n"
            "• <code>Romans 8:28</code>\n"
            "• <code>1 Cor 13:4-7</code>\n\n"
            "I will immediately fetch the verse for you in your preferred translation! 📖"
        )
        await message.answer(prompt_text, parse_mode="HTML", reply_markup=build_theo_reply_keyboard())

    # -------------------------------------------------------------------------
    # BOT-SPECIFIC BUTTON 3: 🔖 Saved Verses
    # -------------------------------------------------------------------------
    @router.message(F.text == "🔖 Saved Verses")
    async def saved_verses_handler(message: Message, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            return
        await send_saved_verses_page(message, services, page=1)

    @router.callback_query(SavedVersesPage.filter())
    async def inline_saved_verses_page(
        callback: CallbackQuery, callback_data: SavedVersesPage, services: ServiceContainer
    ) -> None:
        await callback.answer()
        await send_saved_verses_page(callback, services, page=callback_data.page)

    async def send_saved_verses_page(
        message: Message | CallbackQuery,
        services: ServiceContainer,
        page: int = 1
    ) -> None:
        telegram_user = message.from_user
        user = await services.identity.resolve_telegram_user(telegram_user)

        user_state = await services.users.get_user_state(user["id"], "theo")
        translation = user_state.get("translation", "kjv") if user_state else "kjv"

        verses = await services.users.get_saved_verses(user["id"], "theo")

        is_callback = isinstance(message, CallbackQuery)
        reply_target = message.message if is_callback else message

        if not verses:
            msg = "You have no saved verses yet.\n\nTap <b>💜 Save</b> on any verse to bookmark it here."
            if is_callback:
                await reply_target.edit_text(msg, parse_mode="HTML")
            else:
                await reply_target.answer(msg, parse_mode="HTML", reply_markup=build_theo_reply_keyboard())
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

        parts = [f"<b>🔖 My Saved Verses</b> (Page {page} of {total_pages})"]

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
            nav_row.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=SavedVersesPage(page=page-1).pack()))

        nav_row.append(InlineKeyboardButton(text=f"• {page} / {total_pages} •", callback_data="global_ignore"))

        if page < total_pages:
            nav_row.append(InlineKeyboardButton(text="Next ➡️", callback_data=SavedVersesPage(page=page+1).pack()))

        inline_kb.append(nav_row)
        markup = InlineKeyboardMarkup(inline_keyboard=inline_kb)

        if is_callback:
            await reply_target.edit_text(reply_text, parse_mode="HTML", reply_markup=markup)
        else:
            await reply_target.answer(reply_text, parse_mode="HTML", reply_markup=markup)

    # -------------------------------------------------------------------------
    # ROW 3 SETTINGS BUTTON: 🌐 Translation / /translation
    # -------------------------------------------------------------------------
    @router.message(F.text == "🌐 Translation")
    @router.callback_query(F.data == "theo_translation_menu")
    async def translation_menu_handler(event: Message | CallbackQuery) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event

        if is_callback:
            await event.answer()

        prompt_text = (
            "<b>🌐 Select Bible Translation</b>\n\n"
            "Choose your preferred Bible translation below or use <code>/translation KJV</code>:"
        )
        markup = build_translation_selection_keyboard()
        await message.answer(prompt_text, parse_mode="HTML", reply_markup=markup)

    @router.callback_query(F.data.startswith("theo_set_trans_"))
    async def set_translation_callback(callback: CallbackQuery, services: ServiceContainer) -> None:
        trans_code = callback.data.replace("theo_set_trans_", "").lower()
        if trans_code not in VALID_TRANSLATIONS:
            await callback.answer("Invalid translation option.", show_alert=True)
            return

        user = await services.identity.resolve_telegram_user(callback.from_user)
        state = await services.users.get_user_state(user["id"], "theo")
        state["translation"] = trans_code
        await services.users.set_user_state(user["id"], "theo", state)

        await callback.answer(f"Translation set to {trans_code.upper()}!")
        await callback.message.edit_text(
            f"✅ Bible translation updated to <b>{trans_code.upper()}</b>.",
            parse_mode="HTML"
        )

    @router.message(Command("translation"))
    async def set_translation_command(message: Message, services: ServiceContainer) -> None:
        parts = message.text.split(maxsplit=1) if message.text else []
        if len(parts) < 2:
            await message.answer(
                "Please specify a translation. Example: <code>/translation KJV</code>",
                parse_mode="HTML",
                reply_markup=build_translation_selection_keyboard()
            )
            return

        translation = parts[1].strip().lower()
        if translation not in VALID_TRANSLATIONS:
            options = ", ".join(sorted(VALID_TRANSLATIONS)).upper()
            await message.answer(f"Invalid translation. Choose from: {options}")
            return

        chat = await register_group_chat(message, services, "theo")
        if chat:
            await services.chats.set_bot_settings(
                bot_name="theo",
                chat_id=chat["id"],
                settings={"translation": translation},
            )
            await message.answer(
                f"Theo will now use {translation.upper()} for this group.",
                reply_markup=build_theo_reply_keyboard(),
            )
        else:
            user = await services.identity.resolve_telegram_user(message.from_user)
            state = await services.users.get_user_state(user["id"], "theo")
            state["translation"] = translation
            await services.users.set_user_state(user["id"], "theo", state)
            await message.answer(
                f"Theo will now use {translation.upper()} for your personal messages.",
                reply_markup=build_theo_reply_keyboard(),
            )

    # -------------------------------------------------------------------------
    # SUBSCRIPTION COMMANDS
    # -------------------------------------------------------------------------
    @router.message(Command("subscribe"))
    async def subscribe_command(message: Message, services: ServiceContainer) -> None:
        if message.chat.type == "private":
            user = await services.identity.resolve_telegram_user(message.from_user)
            existing_sub = await services.users.get_subscription(user["id"], "theo", "daily_devotional")
            if existing_sub and existing_sub.get("enabled"):
                await message.answer(
                    "ℹ️ You are already subscribed to Theo's Daily Verse of the Day.",
                    reply_markup=build_theo_reply_keyboard(),
                )
                return

            await services.users.set_subscription(
                user_id=user["id"],
                bot_name="theo",
                subscription_type="daily_devotional",
                enabled=True,
            )
            await message.answer(
                "✅ You are now subscribed to Theo's Daily Verse of the Day. You will receive it daily at 6:00 AM WAT.",
                reply_markup=build_theo_reply_keyboard(),
            )
            return

        chat = await register_group_chat(message, services, "theo")
        if not chat:
            await message.answer("Subscriptions are only supported in groups or private DMs.")
            return

        try:
            member = await message.chat.get_member(message.from_user.id)
            if member.status not in ("administrator", "creator"):
                await message.answer("❌ Only group admins can subscribe the group to daily verses.")
                return
        except Exception:
            pass

        existing_sub = await services.chats.get_subscription("theo", chat["id"], "daily_devotional")
        if existing_sub and existing_sub.get("enabled"):
            await message.answer(
                f"ℹ️ {message.chat.title} is already subscribed to Theo's Daily Verse.",
                reply_markup=build_theo_reply_keyboard(),
            )
            return

        await services.chats.set_subscription(
            bot_name="theo",
            chat_id=chat["id"],
            subscription_type="daily_devotional",
            enabled=True,
        )
        await message.answer(
            f"✅ **{message.chat.title}** is now subscribed to Theo's Daily Verse.",
            parse_mode="Markdown",
            reply_markup=build_theo_reply_keyboard(),
        )

    @router.message(Command("unsubscribe"))
    async def unsubscribe_command(message: Message, services: ServiceContainer) -> None:
        if message.chat.type == "private":
            user = await services.identity.resolve_telegram_user(message.from_user)
            await services.users.set_subscription(
                user_id=user["id"],
                bot_name="theo",
                subscription_type="daily_devotional",
                enabled=False,
            )
            await message.answer(
                "Paused your daily verse subscription. Use /subscribe anytime to resume!",
                reply_markup=build_theo_reply_keyboard(),
            )
            return

        chat = await register_group_chat(message, services, "theo")
        if chat:
            await services.chats.set_subscription(
                bot_name="theo",
                chat_id=chat["id"],
                subscription_type="daily_devotional",
                enabled=False,
            )
            await message.answer("Paused daily verse delivery for this group.")

    # -------------------------------------------------------------------------
    # VERSE CALLBACK ACTIONS (Save / Next Verse)
    # -------------------------------------------------------------------------
    @router.callback_query(VerseAction.filter(F.action == "save"))
    async def handle_save_verse(
        callback: CallbackQuery, callback_data: VerseAction, services: ServiceContainer
    ) -> None:
        user = await services.identity.resolve_telegram_user(callback.from_user)
        reference = callback_data.reference.replace("_", " ")
        saved = await services.users.save_verse(
            user_id=user["id"],
            bot_name="theo",
            reference=reference,
            category=callback_data.category
        )
        if saved:
            await callback.answer("Verse saved to your bookmarks! 💜", show_alert=True)
        else:
            await callback.answer("This verse is already in your saved verses.", show_alert=True)

    @router.callback_query(VerseAction.filter(F.action == "next"))
    async def handle_next_verse(
        callback: CallbackQuery, callback_data: VerseAction, services: ServiceContainer
    ) -> None:
        import random
        from bots.theo.utils.seed_votd import CURATED_REFERENCES

        votd_service = VOTDService(services.supabase)
        user = await services.identity.resolve_telegram_user(callback.from_user)
        user_state = await services.users.get_user_state(user["id"], "theo")
        translation = user_state.get("translation", "kjv") if user_state else "kjv"

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

    # -------------------------------------------------------------------------
    # FALLBACK SCRIPTURE DETECTION (Catch-all for text containing scriptures)
    # -------------------------------------------------------------------------
    @router.message(F.text)
    async def scripture_detection_handler(message: Message, services: ServiceContainer) -> None:
        await handle_bible_detection(message, services)

    return router
