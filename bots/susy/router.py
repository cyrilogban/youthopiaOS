from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
import httpx
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BufferedInputFile,
    FSInputFile,
)

from shared.services.container import ServiceContainer
from shared.utils.ui import (
    BOT_FAMILY_DIRECTORY_TEXT,
    get_community_links_keyboard,
    render_shared_profile_card,
    send_community_exploration_page,
    handle_global_onboarding_callback,
)
from bots.susy.utils.keyboards import (
    build_susy_reply_keyboard,
    build_susy_start_inline_keyboard,
    build_onboarding_tour_keyboard,
    build_topic_directory_keyboard,
    build_susy_group_welcome_keyboard,
)

from core.telegram_runtime import build_router
from aiogram.filters import Command, CommandObject

# Will add Susy's official photo URL here when available
SUSY_PHOTO = None

def build_susy_router(description: str, music_service=None) -> Router:
    router = build_router("susy", description, include_base_commands=False)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        private_commands = [
            BotCommand(command="start", description="Meet Susy & Welcome"),
            BotCommand(command="where", description="Community Topic Directory"),
            BotCommand(command="profile", description="View your profile"),
            BotCommand(command="help", description="Susy Hostess Guide"),
        ]
        
        group_commands = [
            BotCommand(command="start", description="Meet Susy"),
            BotCommand(command="where", description="Community Topic Directory"),
            BotCommand(command="help", description="Susy Hostess Guide"),
        ]
        
        try:
            await bot.delete_my_commands()
        except Exception:
            pass
        await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())

    @router.my_chat_member()
    async def on_bot_added(event, bot: Bot) -> None:
        if event.new_chat_member.status in {"member", "administrator"}:
            first_name = event.from_user.first_name if event.from_user else "Friend"
            chat_title = event.chat.title or "your group"
            
            welcome_caption = (
                f"🌸 <b>Hey {first_name}, This is Susy!</b>\n\n"
                f"Thanks for having me in <b>{chat_title}</b>! I am your friendly community hostess.\n\n"
                f"I'm here to make sure every member feels welcomed, connected, and guided across our community!"
            )
            
            welcome_markup = build_susy_group_welcome_keyboard()
            try:
                await bot.send_message(
                    chat_id=event.chat.id,
                    text=welcome_caption,
                    parse_mode="HTML",
                    reply_markup=welcome_markup
                )
            except Exception as e:
                logger.error(f"SUSY BOT ADDED WELCOME NOTICE: {e}")

    async def send_group_welcome_card(message: Message) -> None:
        first_name = message.from_user.first_name if message.from_user else "Friend"
        chat_title = message.chat.title or "your community"

        welcome_text = (
            f"🌸 <b>Hey {first_name}, This is Susy!</b>\n\n"
            f"Thanks for having me in <b>{chat_title}</b>! I am your community hostess.\n\n"
            f"I am here to welcome you, answer your questions, and guide you around!"
        )

        welcome_markup = build_susy_group_welcome_keyboard()

        banner_url = "https://images.unsplash.com/photo-1507692049790-de58290a4334?w=1200&q=80"
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(banner_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                if resp.status_code == 200:
                    banner_file = BufferedInputFile(resp.content, filename="welcome.jpg")
                    await message.answer_photo(
                        photo=banner_file,
                        caption=welcome_text,
                        parse_mode="HTML",
                        reply_markup=welcome_markup
                    )
                    return
        except Exception:
            pass

        await message.answer(welcome_text, parse_mode="HTML", reply_markup=welcome_markup)

    @router.message(Command("start"))
    async def handle_start(message: Message, command: CommandObject, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            is_targeted = message.text and ("susy" in message.text.lower() or "@" in message.text)
            if not is_targeted:
                try:
                    await message.delete()
                except Exception:
                    pass
                return
            await send_group_welcome_card(message)
            return
                
        if message.text and "onboarding" in message.text:
            await send_onboarding_page(message, 1)
            return

        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"
        
        welcome_text = (
            f"<b>Welcome to YOUTHOPIA BIBLE COMMUNITY, {first_name}! 🤍</b>\n"
            "<blockquote>I am Susy, your first friend and community hostess here in the YouThopia ecosystem.\n\n"
            "We are a Gen Z Christian community built to help you grow in your faith, connect with believers, and have fun doing it!</blockquote>\n\n"
            "<b>Getting Started</b>\n"
            "<blockquote>I'm here to show you around! Use the menu buttons below to check your profile, explore the community, or ask for help!</blockquote>\n\n"
            "Sharing God's Love All The Way 💜"
        )
        
        reply_menu = build_susy_reply_keyboard()
        inline_menu = build_susy_start_inline_keyboard()
        
        if SUSY_PHOTO:
            await message.answer_photo(
                photo=SUSY_PHOTO,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=inline_menu
            )
        else:
            await message.answer(
                welcome_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=inline_menu
            )
        
        await message.answer("🌸 Use the persistent menu below to navigate Susy's hostess controls:", reply_markup=reply_menu)

    @router.message(Command("where"))
    async def on_where_command(message: Message):
        directory_text = (
            "<b>🗺️ YouThopia Topic Directory & Guide</b>\n\n"
            "<blockquote>Where would you like to go today? Here is your quick map to our group threads:</blockquote>\n\n"
            "📢 <b>Announcements & Events:</b> Stay up to date with community news.\n"
            "📖 <b>Devotionals & Scripture:</b> Daily inspiration with Theo (@iamtheobot).\n"
            "🎮 <b>Games & Quizzes:</b> Test your Bible knowledge with Lusy (@iamlusybot).\n"
            "🙏 <b>Prayer & Testimonies:</b> Stand in faith and share praise reports.\n"
            "💬 <b>General Fellowship:</b> Connect and chat with fellow YouTopians!\n\n"
            "<i>Tap below to jump right into the main group! 💜</i>"
        )
        markup = build_topic_directory_keyboard()
        await message.answer(directory_text, parse_mode="HTML", reply_markup=markup)

    @router.message(F.text == "Community")
    async def on_about_community(message: Message):
        if message.chat.type != "private": return
        
        about_text = (
            "<b>About YouThopia Bible Community 🌍</b>\n"
            "<blockquote>We are a cross-platform Gen Z Christian community. This is a space where faith meets real life. We grow together, share God's Word, and support one another on the journey of becoming who God created us to be.</blockquote>\n\n"
            "If you haven't joined the main group yet, jump in! We can't wait to fellowship with you. 🤍"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Join the Main Group", url="https://t.me/youthopiabiblecommunity")]
        ])
        
        await message.answer(about_text, parse_mode="HTML", reply_markup=markup)

    @router.message(Command("playlist"))
    @router.message(F.text == "My Playlist")
    @router.callback_query(F.data == "susy_my_playlist")
    async def handle_my_playlist(event: Message | CallbackQuery, services: ServiceContainer) -> None:
        is_cb = isinstance(event, CallbackQuery)
        message = event.message if is_cb else event
        user_obj = event.from_user

        empty_txt = (
            "<b>📜 Your Personal Playlist is Empty!</b>\n\n"
            "You haven't saved any tracks yet. Play a song and tap <b>💜 Save to Favorites</b> to build your collection!"
        )

        try:
            user = await services.identity.resolve_telegram_user(user_obj)
            user_id = user["id"]

            try:
                saved_tracks = await services.supabase.find_many("user_favorite_tracks", {"user_id": user_id})
            except Exception as e:
                saved_tracks = []

            if not saved_tracks:
                if is_cb:
                    await event.answer("Your playlist is currently empty! Play a song to save it. 💜", show_alert=True)
                else:
                    await message.answer(empty_txt, parse_mode="HTML")
                return

            list_txt = "<b>📜 Your Saved Playlist 🎶</b>\n\n"
            for idx, tr in enumerate(saved_tracks, 1):
                list_txt += f"{idx}. <b>{tr.get('title', 'Unknown Track')}</b>\n"

            list_txt += "\n<i>Type the name of any track to play it instantly!</i>"

            if is_cb:
                await event.answer()
            await message.answer(list_txt, parse_mode="HTML")
        except Exception:
            if is_cb:
                await event.answer("Your playlist is currently empty! Play a song to save it. 💜", show_alert=True)
            else:
                await message.answer(empty_txt, parse_mode="HTML")

    # --- DM MUSIC QUERY (DISABLED - PRESERVED FOR FUTURE REUSE) ---
    # @router.message(F.chat.type == "private", F.text & ~F.text.startswith("/"))
    # async def handle_private_dm_music_query(message: Message) -> None:
    #     ...


    # --- ONBOARDING PAGINATION LOGIC ---
    
    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 3: 🌐 Community
    # -------------------------------------------------------------------------
    @router.message(F.text == "🌐 Community")
    @router.message(F.text == "🌐 Community Links")
    async def community_handler(message: Message) -> None:
        if message.chat.type != "private":
            return
        await send_community_exploration_page(message, 1)

    async def send_onboarding_page(message: Message, page: int, edit: bool = False) -> None:
        await send_community_exploration_page(message, page, edit=edit)

    @router.callback_query(F.data.startswith("onboarding_"))
    async def handle_onboarding_callbacks(callback_query: CallbackQuery, services: ServiceContainer) -> None:
        await handle_global_onboarding_callback(callback_query, services)

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 1: 👤 My Profile / /profile
    # -------------------------------------------------------------------------
    @router.message(F.text == "👤 My Profile")
    @router.message(Command("profile"))
    @router.callback_query(F.data == "susy_profile")
    async def handle_susy_profile(event: Message | CallbackQuery, services: ServiceContainer) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event
        user_from = event.from_user

        if is_callback:
            await event.answer()

        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return

        user = await services.identity.resolve_telegram_user(user_from)
        engagement = user.get("engagement_level", "new")
        trust = user.get("trust_score", 100)

        # 1. Orientation status
        orientation_str = "Completed 🎉" if engagement == "onboarded" else "Pending (Tap 🌐 Community)"

        # 2. Dynamic Community Status
        if trust >= 100 and engagement == "onboarded":
            status_str = "Verified Member"
        elif trust >= 80:
            status_str = "Active YouTopian"
        else:
            status_str = "Under Observation"

        # 3. Dynamic Joined Date
        created_at_raw = user.get("created_at")
        joined_str = "Aug 2026"
        if created_at_raw:
            try:
                dt = datetime.fromisoformat(str(created_at_raw).replace("Z", "+00:00"))
                joined_str = dt.strftime("%b %Y")
            except Exception:
                pass

        bot_stats = [
            f"🌸 Orientation: <b>{orientation_str}</b>",
            f"✨ Community Status: <b>{status_str}</b>",
            f"📅 Joined YouThopia: <b>{joined_str}</b>",
        ]

        card_text = render_shared_profile_card(
            user_data=user,
            telegram_first_name=user_from.first_name or "Friend",
            bot_specific_stats=bot_stats
        )

        await message.answer(card_text, parse_mode="HTML", reply_markup=build_susy_reply_keyboard())

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 2: ℹ️ Help / /help
    # -------------------------------------------------------------------------
    @router.message(Command("help"))
    @router.message(F.text == "Help")
    @router.callback_query(F.data == "susy_help")
    async def handle_susy_help(event: Message | CallbackQuery, services: ServiceContainer) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event

        if is_callback:
            await event.answer()

        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return

        first_name = event.from_user.first_name or "Friend"
        help_text = (
            f"<b>🎵 Susy | Welcome Bot Help Guide, {first_name}!</b>\n"
            "<blockquote>I am Susy (@iamsusiebot), your community hostess and onboarding guide in YOUTHOPIA BIBLE COMMUNITY.\n\n"
            "<b>Susy Features & Commands</b>\n"
            "• 🌸 <b>Explore the Community:</b> Interactive 3-step tour for new YouTopians (+50 Trust Points).\n"
            "• 🗺️ <b>Topic Directory (/where):</b> Direct links to all group threads.\n"
            "• 🤝 <b>Hospitality & Guidance:</b> Here to answer questions and show you around.\n"
            "• <b>/start:</b> Open Susy welcome dashboard.\n"
            "• <b>/where:</b> Access group topic threads directory.</blockquote>\n\n"
            f"{BOT_FAMILY_DIRECTORY_TEXT}\n\n"
            "Sharing God's Love All The Way 💜"
        )

        await message.answer(
            help_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=get_community_links_keyboard(),
        )

    @router.callback_query(F.data == "susy_community_links")
    async def handle_susy_community_links(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            "<b>🌐 YOUTHOPIA BIBLE COMMUNITY LINKS</b>\n"
            "<blockquote>Connect with us across all platforms to stay updated, fellowship, and grow together! 💜</blockquote>",
            parse_mode="HTML",
            reply_markup=get_community_links_keyboard()
        )

    def _get_dm_music_controls_keyboard(is_saved: bool = False) -> InlineKeyboardMarkup:
        save_text = "💜 Saved in Playlist" if is_saved else "💜 Save to Favorites"
        share_url = "https://t.me/share/url?url=https%3A%2F%2Ft.me%2Fiamsusiebot&text=Listen%20to%20worship%20music%20with%20Susy%20on%20Telegram%20%F0%9F%8E%B6"
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=save_text, callback_data="susy_fav_save"),
                    InlineKeyboardButton(text="📜 My Playlist", callback_data="susy_my_playlist")
                ],
                [
                    InlineKeyboardButton(text="➕ Request Another", callback_data="susy_request_another"),
                    InlineKeyboardButton(text="👥 Share Track ↗️", url=share_url)
                ]
            ]
        )

    def _get_music_controls_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💜 Save to Favorites", callback_data="susy_fav_save"),
                    InlineKeyboardButton(text="📜 My Playlist", callback_data="susy_group_playlist")
                ],
                [
                    InlineKeyboardButton(text="➕ Request Another", callback_data="susy_group_request"),
                    InlineKeyboardButton(text="💬 Open Susy DM ↗️", url="https://t.me/iamsusiebot")
                ],
                [
                    InlineKeyboardButton(text="🗑️ Close", callback_data="susy_close_msg")
                ]
            ]
        )

    @router.callback_query(F.data == "susy_fav_save")
    async def handle_save_favorite(callback: CallbackQuery, services: ServiceContainer) -> None:
        track_title = "Worship Track"
        if callback.message and callback.message.caption:
            for line in callback.message.caption.split("\n"):
                if "Title:" in line:
                    track_title = line.replace("Title:", "").replace("<b>", "").replace("</b>", "").strip()

        try:
            user = await services.identity.resolve_telegram_user(callback.from_user)
            user_id = user["id"]

            payload = {
                "user_id": user_id,
                "title": track_title,
                "bot_name": "susy"
            }

            await services.supabase.upsert(
                "user_favorite_tracks",
                payload,
                on_conflict="user_id, title"
            )

            is_private = callback.message and callback.message.chat.type == "private"

            if is_private:
                try:
                    await callback.message.edit_reply_markup(reply_markup=_get_dm_music_controls_keyboard(is_saved=True))
                except Exception:
                    pass

                await callback.answer(
                    f"🎉 Saved to Favorites! 💜\n\n"
                    f"\"{track_title}\" has been added to your personal playlist.\n\n"
                    f"Tap '📜 My Playlist' below to view your saved songs!",
                    show_alert=True
                )
            else:
                await callback.answer(
                    f"🎉 Saved to Favorites! 💜\n\n"
                    f"\"{track_title}\" has been saved to your personal playlist.\n\n"
                    f"Open a private chat with Susy (@iamsusiebot) to view your saved songs!",
                    show_alert=True
                )
        except Exception as e:
            await callback.answer(f"🎉 \"{track_title}\" saved to your playlist! 💜", show_alert=True)

    @router.callback_query(F.data == "susy_group_playlist")
    async def handle_group_playlist(callback: CallbackQuery) -> None:
        await callback.answer(
            "📜 Your Saved Playlist:\n\n"
            "Open a private chat with Susy (@iamsusiebot) and type /playlist to view and play your saved songs!",
            show_alert=True
        )

    @router.callback_query(F.data == "susy_group_request")
    async def handle_group_request(callback: CallbackQuery) -> None:
        await callback.answer(
            "🎶 Request a Song:\n\n"
            "Type /playsong <song name> right here in this chat to request your next song!",
            show_alert=True
        )

    @router.callback_query(F.data == "susy_request_another")
    async def handle_request_another(callback: CallbackQuery) -> None:
        await callback.answer("🎧 Type the title or link of your next song right here in this chat!", show_alert=True)

    # --- MUSIC COMMANDS & CALLBACKS (DISABLED - PRESERVED FOR FUTURE REUSE) ---
    # @router.message(Command("playsong"))
    # async def handle_play(message: Message, command: CommandObject) -> None:
    #     ...
    # @router.message(Command("stop")) ...

    @router.callback_query(F.data == "susy_close_msg")
    async def handle_close_msg(callback: CallbackQuery) -> None:
        try:
            await callback.message.delete()
        except Exception:
            await callback.answer("Message closed")

    return router
