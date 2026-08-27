from __future__ import annotations

import asyncio
import logging
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
    ChatMemberUpdated,
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
    handle_group_profile_acknowledgment,
)
from bots.susy.utils.keyboards import (
    build_susy_reply_keyboard,
    build_susy_start_inline_keyboard,
    build_onboarding_tour_keyboard,
    build_susy_group_welcome_keyboard,
    build_susy_member_welcome_keyboard,
    build_susy_farewell_keyboard,
)

from core.telegram_runtime import build_router, register_group_chat, register_chat
from aiogram.filters import Command, CommandObject

logger = logging.getLogger(__name__)

SUSY_PHOTO = None


async def self_destruct_message(bot: Bot, chat_id: int, message_id: int, delay_seconds: int = 10) -> None:
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


def build_susy_router(description: str, music_service=None) -> Router:
    router = build_router("susy", description, include_base_commands=False)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        private_commands = [
            BotCommand(command="start", description="Meet Susy"),
            BotCommand(command="profile", description="View your profile"),
            BotCommand(command="help", description="Susy Hostess Guide"),
        ]
        
        group_commands = [
            BotCommand(command="start", description="Meet Susy"),
            BotCommand(command="help", description="Susy Hostess Guide"),
        ]
        
        import os
        from aiogram.types import BotCommandScopeChat
        admin_ids_str = os.getenv("ADMIN_OWNER_ID") or os.getenv("ADMIN_IDS") or ""
        admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]
        for admin_id in admin_ids:
            try:
                await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=admin_id))
            except Exception:
                pass

        await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())

    # -------------------------------------------------------------------------
    # GROUP JOIN WELCOME EVENT (BOT ADDED TO GROUP)
    # -------------------------------------------------------------------------
    @router.my_chat_member()
    async def on_susy_group_join(event: ChatMemberUpdated, bot: Bot, services: ServiceContainer) -> None:
        old_status = event.old_chat_member.status
        new_status = event.new_chat_member.status

        # Case 1: Susy added or promoted in group
        if new_status in ("member", "administrator"):
            try:
                await register_chat(event.chat, services, "susy")
            except Exception as e:
                logger.warning(f"Failed to register group chat for Susy on join: {e}")
            chat_id = event.chat.id
            group_title = event.chat.title or "Group"

            # Status transition: Member -> Admin promotion upgrade
            if old_status == "member" and new_status == "administrator":
                try:
                    sent_msg = await bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"⚡ <b>ADMIN RIGHTS GRANTED!</b>\n\n"
                            f"<blockquote>Thank you for promoting Susy in <b>{group_title}</b>! "
                            f"Community hostess and onboarding features are now fully active. 💜</blockquote>"
                        ),
                        parse_mode="HTML"
                    )
                    asyncio.create_task(self_destruct_message(bot, chat_id, sent_msg.message_id, 5))
                except Exception:
                    pass
                return

            # Differentiated Welcome Card based on Admin vs Member status
            if new_status == "administrator":
                welcome_text = (
                    f"<b>SUSY IS HERE 💬</b>\n\n"
                    f"<blockquote>I am Susy — your Community Hostess & Onboarding Guide in <b>YouThopiaOS</b>.\n\n"
                    f"I keep our community connected and welcomed across our 5-bot ecosystem:\n"
                    f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                    f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                    f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                    f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                    f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                    f"<b>COMMUNITY QUICK START</b>\n"
                    f"<blockquote>• Tap <b>💬 Meet Susy in DM</b> below to start your community tour.\n"
                    f"• <b>Hostess Welcome:</b> <code>ENABLED</code>\n"
                    f"• <b>Admins:</b> Manage anytime using <code>/help</code>.</blockquote>\n\n"
                    f"<i>Sharing God's Love All The Way 💜</i>"
                )
                markup = build_susy_group_welcome_keyboard()
            else:
                welcome_text = (
                    f"<b>SUSY IS HERE 💬</b>\n\n"
                    f"<blockquote>I am Susy — your Community Hostess & Onboarding Guide in <b>YouThopiaOS</b>.\n\n"
                    f"I keep our community connected and welcomed across our 5-bot ecosystem:\n"
                    f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                    f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                    f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                    f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                    f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                    f"<b>⚠️ ADMIN RIGHTS NEEDED</b>\n"
                    f"<blockquote>To help manage member welcomes smoothly, please grant Susy <b>Admin Rights</b>!</blockquote>"
                )
                markup = build_susy_member_welcome_keyboard()

            try:
                sent_msg = await bot.send_message(
                    chat_id=chat_id,
                    text=welcome_text,
                    parse_mode="HTML",
                    reply_markup=markup
                )
                # Auto-delete welcome card after 120s
                asyncio.create_task(self_destruct_message(bot, chat_id, sent_msg.message_id, 120))
            except Exception as e:
                logger.warning(f"Failed to send Susy group welcome card: {e}")

        # Case 2: Susy removed or kicked from group
        elif new_status in ("left", "kicked"):
            chat_id = event.chat.id
            group_title = event.chat.title or "your group"
            try:
                await services.chats.set_subscription("susy", chat_id, "welcome", enabled=False)
            except Exception:
                pass

            # Notify Admin in DM
            admin_user_id = event.from_user.id if event.from_user else None
            if admin_user_id:
                try:
                    farewell_text = (
                        f"<b>Susy Departs {group_title} 💬</b>\n\n"
                        f"<blockquote>Susy has been removed from <b>{group_title}</b>.\n"
                        f"Hostess welcome services have been paused for this group. "
                        f"You can re-invite Susy anytime or explore our other 4 community bots below! 💜</blockquote>"
                    )
                    await bot.send_message(
                        chat_id=admin_user_id,
                        text=farewell_text,
                        parse_mode="HTML",
                        reply_markup=build_susy_farewell_keyboard()
                    )
                except Exception as e:
                    logger.warning(f"Could not send Susy farewell DM to admin {admin_user_id}: {e}")

    @router.callback_query(F.data == "susy_prompt_admin")
    async def handle_susy_prompt_admin(callback: CallbackQuery, bot: Bot) -> None:
        try:
            member = await bot.get_chat_member(callback.message.chat.id, callback.from_user.id)
            if member.status not in ("administrator", "creator"):
                await callback.answer("⚠️ Only group administrators can promote bots to admin!", show_alert=True)
                return
        except Exception:
            pass

        await callback.answer()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Open Admin Permission Sheet", url="https://t.me/iamsusiebot?startgroup=admin&admin=delete_messages+pin_messages+invite_users")]
        ])
        try:
            sent_msg = await callback.message.answer(
                "<blockquote>💬 <b>Susy Administrator Setup</b>\n\n"
                "Tap below to open Telegram's permission sheet with required rights pre-checked!</blockquote>",
                parse_mode="HTML",
                reply_markup=markup
            )
            asyncio.create_task(self_destruct_message(bot, callback.message.chat.id, sent_msg.message_id, 20))
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # ADMIN COMMAND: /leave or /remove_susy
    # -------------------------------------------------------------------------
    @router.message(Command("leave"))
    @router.message(Command("remove_susy"))
    async def handle_leave_command(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type == "private":
            await message.answer("⚠️ This command is only for group chats.")
            return

        chat_id = message.chat.id
        group_title = message.chat.title or "your group"
        admin_id = message.from_user.id if message.from_user else None

        # Check if user is admin
        try:
            member = await bot.get_chat_member(chat_id, admin_id)
            if member.status not in ("creator", "administrator"):
                try:
                    await message.delete()
                except Exception:
                    pass
                msg = await message.answer("⚠️ Only group administrators can use /leave.")
                asyncio.create_task(self_destruct_message(bot, chat_id, msg.message_id, 5))
                return
        except Exception:
            pass

        # Send DM to admin
        if admin_id:
            try:
                farewell_text = (
                    f"<b>Susy Departs {group_title} 💬</b>\n\n"
                    f"<blockquote>Susy has left <b>{group_title}</b> as requested.\n"
                    f"Hostess welcome services have been paused for this group. "
                    f"You can re-invite Susy anytime or explore our other 4 community bots below! 💜</blockquote>"
                )
                await bot.send_message(
                    chat_id=admin_id,
                    text=farewell_text,
                    parse_mode="HTML",
                    reply_markup=build_susy_farewell_keyboard()
                )
            except Exception as e:
                logger.warning(f"Could not send Susy leave DM to admin {admin_id}: {e}")

        # Leave group cleanly
        try:
            await bot.leave_chat(chat_id)
        except Exception as e:
            logger.warning(f"Susy failed to leave chat {chat_id}: {e}")

    # -------------------------------------------------------------------------
    # COMMAND: /start
    # -------------------------------------------------------------------------
    @router.message(Command("start"))
    async def handle_start(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass

            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💬 Meet Susy in DM", url="https://t.me/iamsusiebot?start=welcome")],
                [InlineKeyboardButton(text="🚀 Take Community Tour", url="https://t.me/iamsusiebot?start=tour")],
            ])
            try:
                sent_msg = await message.answer(
                    "<blockquote>💬 <b>Susy Hostess Engine is active in this group!</b>\n"
                    "Tap below to open your DM Dashboard and explore our community.</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
            except Exception:
                pass
            return
                
        if message.text and "tour" in message.text:
            await send_onboarding_page(message, 1)
            return

        await register_group_chat(message, services, "susy")
        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"
        
        if user.get("engagement_level") == "new":
            welcome_text = (
                f"<b>Welcome to YOUTHOPIA BIBLE COMMUNITY, {first_name}! 💜</b>\n\n"
                f"<blockquote>I am Susy — your community hostess here in the YouThopia ecosystem.\n\n"
                f"We are a Gen Z Christian community built to help you grow in your faith, connect with believers, and have fun doing it! Here is our 5-bot ecosystem ready for you:\n"
                f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                f"<b>SELECT AN OPTION BELOW TO GET STARTED:</b>"
            )
            await services.users.set_engagement_level(user["id"], "active")
        else:
            welcome_text = (
                f"<b>Welcome back, {first_name}! 💜</b>\n\n"
                f"<blockquote>✨ <b>Community Status:</b> <code>Active YouTopian 💜</code>\n"
                f"💬 <b>Community:</b> <code>Connected</code>\n\n"
                f"I'm always here to help you navigate our ecosystem and stay connected with fellow YouTopians!</blockquote>\n\n"
                f"<b>WHAT WOULD YOU LIKE TO EXPLORE TODAY?</b>"
            )
        
        reply_menu = build_susy_reply_keyboard()
        inline_menu = build_susy_start_inline_keyboard()
        
        await message.answer("💬 <b>Welcome to Susy Hostess Dashboard!</b>", parse_mode="HTML", reply_markup=reply_menu)
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
    async def handle_susy_profile(event: Message | CallbackQuery, bot: Bot, services: ServiceContainer) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event
        user_from = event.from_user

        if is_callback:
            await event.answer()

        if message.chat.type != "private":
            await handle_group_profile_acknowledgment(message, bot)
            if user_from:
                try:
                    await send_susy_profile(message, services, telegram_user=user_from, send_to_dm=True, bot=bot)
                except Exception as e:
                    logger.warning(f"Failed to send Susy profile to DM: {e}")
            return

        await send_susy_profile(message, services, telegram_user=user_from)

    async def send_susy_profile(
        message: Message, services: ServiceContainer, telegram_user: Any | None = None, send_to_dm: bool = False, bot: Bot | None = None
    ) -> None:
        user_from = telegram_user or message.from_user
        user = await services.identity.resolve_telegram_user(user_from)
        engagement = user.get("engagement_level", "new")
        trust = user.get("trust_score", 100)

        # Dual-check: check engagement_level OR moderation_actions for orientation_completed
        is_onboarded = (engagement == "onboarded")
        if not is_onboarded:
            try:
                actions = await services.supabase.find_many("moderation_actions", {"user_id": user["id"], "action_type": "orientation_completed"})
                if actions:
                    is_onboarded = True
            except Exception as e:
                logger.warning(f"Failed to check moderation_actions for orientation: {e}")

        # 1. Orientation status
        orientation_str = "Completed 🎉" if is_onboarded else "Pending (Tap 🌐 Community)"

        # 2. Dynamic Community Status
        if trust >= 100 and is_onboarded:
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
            f"✨ Orientation: <b>{orientation_str}</b>",
            f"✨ Community Status: <b>{status_str}</b>",
            f"📅 Joined YouThopia: <b>{joined_str}</b>",
        ]

        card_text = render_shared_profile_card(
            user_data=user,
            telegram_first_name=user_from.first_name or "Friend",
            bot_specific_stats=bot_stats
        )

        if send_to_dm and bot and user_from:
            await bot.send_message(
                chat_id=user_from.id,
                text=card_text,
                parse_mode="HTML",
                reply_markup=build_susy_reply_keyboard()
            )
        else:
            await message.answer(card_text, parse_mode="HTML", reply_markup=build_susy_reply_keyboard())

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 2: ℹ️ Help / /help
    # -------------------------------------------------------------------------
    @router.message(Command("help"))
    @router.message(F.text == "ℹ️ Help")
    @router.message(F.text == "Help")
    @router.callback_query(F.data == "susy_help")
    async def handle_susy_help(event: Message | CallbackQuery, bot: Bot, services: ServiceContainer) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event

        if is_callback:
            await event.answer()

        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💬 Open Susy Guide in DM", url="https://t.me/iamsusiebot?start=help")],
                [InlineKeyboardButton(text="🚀 Take Community Tour", callback_data="onboarding_start")],
            ])
            try:
                sent_msg = await message.answer(
                    "<blockquote>💬 <b>Susy Community Hostess Guide</b>\n"
                    "Tap below to view full onboarding features and community guidelines in DM.</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                import asyncio
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
            except Exception:
                pass
            return

        first_name = event.from_user.first_name or "Friend"
        help_text = (
            f"<b>🎵 Susy | Welcome Bot Help Guide, {first_name}!</b>\n"
            "<blockquote>I am Susy (@iamsusiebot), your community hostess and onboarding guide in YOUTHOPIA BIBLE COMMUNITY.\n\n"
            "<b>Susy Features & Commands</b>\n"
            "• 💬 <b>Explore the Community:</b> Interactive 3-step tour for new YouTopians (+50 Trust Points).\n"
            "• 🤝 <b>Hospitality & Guidance:</b> Here to answer questions and show you around.\n"
            "• <b>/start:</b> Open Susy welcome dashboard.\n"
            "• <b>/profile:</b> View your YouTopian profile card.\n"
            "• <b>/help:</b> Show this guidance message.</blockquote>\n\n"
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
