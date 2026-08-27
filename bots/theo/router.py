from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from core.telegram_runtime import build_router, register_group_chat, register_chat
from shared.services.container import ServiceContainer
from shared.utils.ui import (
    BOT_FAMILY_DIRECTORY_TEXT,
    get_community_links_keyboard,
    render_shared_profile_card,
    send_community_exploration_page,
    handle_global_onboarding_callback,
)
from bots.theo.handlers.messages import handle_bible_detection
from bots.theo.services.devotional_service import VOTDService
from bots.theo.utils.keyboards import (
    SavedVersesPage,
    VerseAction,
    build_theo_reply_keyboard,
    build_theo_welcome_inline_keyboard,
    build_theo_group_welcome_keyboard,
    build_theo_member_welcome_keyboard,
    build_theo_farewell_keyboard,
    build_verse_actions_keyboard,
)

logger = logging.getLogger(__name__)

VALID_TRANSLATIONS = {"kjv", "asv", "web", "bbe"}


async def self_destruct_message(bot: Any, chat_id: int, message_id: int, delay_seconds: int = 10) -> None:
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
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

    @router.startup()
    async def on_startup(bot: Bot, services: ServiceContainer) -> None:
        private_commands = [
            BotCommand(command="start", description="Wake Up Theo"),
            BotCommand(command="help", description="Show help information"),
            BotCommand(command="subscribe", description="Subscribe to daily verses"),
            BotCommand(command="unsubscribe", description="Unsubscribe from daily verses"),
        ]
        admin_private_commands = private_commands + [
            BotCommand(command="send_votd", description="Send Today's Verse (Admin)"),
        ]
        group_commands = [
            BotCommand(command="start", description="Wake Up Theo"),
            BotCommand(command="help", description="Show help information"),
        ]

        try:
            await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
            await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())

            import os
            from aiogram.types import BotCommandScopeChat
            admin_ids_str = os.getenv("ADMIN_OWNER_ID") or os.getenv("ADMIN_IDS") or ""
            admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]
            for admin_id in admin_ids:
                try:
                    await bot.set_my_commands(admin_private_commands, scope=BotCommandScopeChat(chat_id=admin_id))
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Failed to set Theo commands: {e}")

        from bots.theo.services.scheduler import setup_theo_scheduler
        setup_theo_scheduler(bot, services)

        # Backfill: Auto-subscribe all existing users and chats in Supabase to Theo's VOTD
        try:
            users = await services.supabase.find_many("users", {})
            for u in users:
                user_id = u["id"]
                sub = await services.users.get_subscription(user_id, "theo", "daily_devotional")
                if not sub:
                    await services.users.set_subscription(user_id, "theo", "daily_devotional", enabled=True)

            chats = await services.supabase.find_many("telegram_chats", {})
            for c in chats:
                chat_id = c["id"]
                sub = await services.chats.get_subscription("theo", chat_id, "daily_devotional")
                if not sub:
                    await services.chats.set_subscription("theo", chat_id, "daily_devotional", enabled=True)
            logger.info("Theo startup: Successfully backfilled VOTD subscriptions for all users and chats.")
        except Exception as e:
            logger.warning(f"Theo startup backfill warning: {e}")

    # -------------------------------------------------------------------------
    # ADMIN COMMAND: /send_votd or /broadcast_votd
    # -------------------------------------------------------------------------
    @router.message(Command("send_votd"))
    @router.message(Command("broadcast_votd"))
    async def handle_manual_votd_broadcast(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            return

        import os
        admin_ids_str = os.getenv("ADMIN_OWNER_ID") or os.getenv("ADMIN_IDS") or ""
        admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]

        if not message.from_user or message.from_user.id not in admin_ids:
            await message.answer("⚠️ Only system administrators can trigger manual VOTD broadcasts.")
            return

        from bots.theo.services.scheduler import trigger_daily_votd
        msg = await message.answer("🔄 Initiating Verse of the Day broadcast...")
        res = await trigger_daily_votd(bot, services)
        await msg.edit_text(f"✅ VOTD Broadcast Complete:\n<code>{res}</code>", parse_mode="HTML")

    # -------------------------------------------------------------------------
    # COMMAND: /start
    # -------------------------------------------------------------------------
    @router.message(Command("start"))
    async def start(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass

            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🚀 Open Private Dashboard", url="https://t.me/iamtheobot?start=dashboard"),
                    InlineKeyboardButton(text="🔍 Search Scripture", callback_data="theo_search_scripture"),
                ]
            ])
            try:
                sent_msg = await message.answer(
                    "<blockquote>📖 <b>Theo Devotional Engine is active in this group!</b>\n"
                    "Type any Bible reference in chat (e.g. <code>John 3:16</code>), or tap below to open your DM Dashboard.</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
            except Exception:
                pass
            return

        await register_group_chat(message, services, "theo")
        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"

        # Auto-subscribe user to Theo's Daily Verse of the Day on /start
        try:
            existing_sub = await services.users.get_subscription(user["id"], "theo", "daily_devotional")
            if not existing_sub:
                await services.users.set_subscription(user["id"], "theo", "daily_devotional", enabled=True)
        except Exception as e:
            logger.warning(f"Failed to auto-subscribe user {user['id']} on /start: {e}")

        sub = await services.users.get_subscription(user["id"], "theo", "daily_devotional")
        sub_status = "ENABLED (6:00 AM)" if (sub and sub.get("enabled")) else "DISABLED"

        state = await services.users.get_user_state(user["id"], "theo")
        translation = state.get("translation", "kjv").upper()

        if user.get("engagement_level") == "new":
            welcome_text = (
                f"<b>Welcome to Daily Scripture, {first_name}! 📖</b>\n\n"
                f"<blockquote>I am Theo — your Daily Word & Scripture Companion in <b>YouThopiaOS</b>.\n\n"
                f"Here in our community, we stay anchored in God's Word every day! Every YouTopian has access to daily devotionals and instant verse lookups across all 5 YouThopiaOS pillar bots:\n"
                f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                f"<b>SEARCH OR EXPLORE BELOW:</b>"
            )
            await services.users.set_engagement_level(user["id"], "active")
        else:
            welcome_text = (
                f"<b>Welcome back, {first_name}! 📖</b>\n\n"
                f"<blockquote>📖 <b>Translation:</b> <code>{translation}</code>\n"
                f"🌅 <b>Daily Verse:</b> <code>{sub_status}</code>\n\n"
                f"Ready to explore God's Word today? Type any verse reference directly in this chat!</blockquote>\n\n"
                f"<b>SEARCH OR EXPLORE BELOW:</b>"
            )

        reply_menu = build_theo_reply_keyboard()
        inline_menu = build_theo_welcome_inline_keyboard()

        await message.answer("📖 <b>Welcome to Theo Devotional Dashboard!</b>", parse_mode="HTML", reply_markup=reply_menu)
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

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 1: 👤 My Profile / /profile
    # -------------------------------------------------------------------------
    @router.message(F.text == "👤 My Profile")
    @router.message(Command("profile"))
    async def profile_handler(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass

            user_first = message.from_user.first_name if message.from_user else "Friend"
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="👤 View Profile in DM", url="https://t.me/iamtheobot?start=profile"),
                    InlineKeyboardButton(text="🔍 Search Scripture", callback_data="theo_search_scripture"),
                ]
            ])
            try:
                sent_msg = await message.answer(
                    f"<blockquote>👤 <b>{user_first}</b>, your scripture profile has been sent to your private DM!</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 5))
            except Exception:
                pass

            if message.from_user:
                try:
                    await send_theo_profile(message, services, telegram_user=message.from_user, send_to_dm=True, bot=bot)
                except Exception as e:
                    logger.warning(f"Failed to send Theo profile to DM for user {message.from_user.id}: {e}")
            return

        await send_theo_profile(message, services)

    @router.callback_query(F.data == "theo_profile")
    async def inline_profile_handler(callback: CallbackQuery, services: ServiceContainer) -> None:
        await callback.answer()
        await send_theo_profile(callback.message, services, telegram_user=callback.from_user)

    async def send_theo_profile(
        message: Message, services: ServiceContainer, telegram_user: Any | None = None, send_to_dm: bool = False, bot: Bot | None = None
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

        if send_to_dm and bot and user_from:
            await bot.send_message(
                chat_id=user_from.id,
                text=card_text,
                parse_mode="HTML",
                reply_markup=build_theo_reply_keyboard()
            )
        else:
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
    async def help_handler(message: Message, bot: Bot) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="📖 Open Theo Guide in DM", url="https://t.me/iamtheobot?start=help"),
                    InlineKeyboardButton(text="🔍 Search Scripture", callback_data="theo_search_scripture"),
                ]
            ])
            try:
                sent_msg = await message.answer(
                    "<blockquote>📖 <b>Theo Devotional Help Guide</b>\n"
                    "Tap below to view full features and community guide in DM.</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
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
    # GROUP JOIN WELCOME EVENT (BOT ADDED TO GROUP)
    # -------------------------------------------------------------------------
    @router.my_chat_member()
    async def on_theo_group_join(event: ChatMemberUpdated, bot: Bot, services: ServiceContainer) -> None:
        old_status = event.old_chat_member.status
        new_status = event.new_chat_member.status

        # Case 1: Theo added or promoted in group
        if new_status in ("member", "administrator"):
            await register_chat(event.chat, services, "theo")
            chat_id = event.chat.id
            group_title = event.chat.title or "Group"

            # Auto-subscribe group to Theo's VOTD on join
            try:
                sub = await services.chats.get_subscription("theo", chat_id, "daily_devotional")
                if not sub:
                    await services.chats.set_subscription("theo", chat_id, "daily_devotional", enabled=True)
            except Exception as e:
                logger.warning(f"Failed to auto-subscribe group {chat_id} on join: {e}")

            # Status transition: Member -> Admin promotion upgrade
            if old_status == "member" and new_status == "administrator":
                try:
                    sent_msg = await bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"⚡ <b>ADMIN RIGHTS GRANTED!</b>\n\n"
                            f"<blockquote>Thank you for promoting Theo in <b>{group_title}</b>! "
                            f"Daily Verses will be delivered clean and automated every morning at 6:00 AM. 📖</blockquote>"
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
                    f"<b>THEO IS HERE 📖</b>\n\n"
                    f"<blockquote>I am Theo — your Daily Word & Scripture Companion in <b>YouThopiaOS</b>.\n\n"
                    f"I keep our community anchored in God's Word across our 5-bot ecosystem:\n"
                    f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                    f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                    f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                    f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                    f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                    f"<b>GROUP QUICK START</b>\n"
                    f"<blockquote>• Type any Bible reference in chat (e.g. <code>John 3:16</code>).\n"
                    f"• <b>Daily Verse:</b> <code>ENABLED</code> (Delivered daily at 6:00 AM).\n"
                    f"• <b>Admins:</b> Manage anytime using <code>/subscribe</code> or <code>/unsubscribe</code>.</blockquote>\n\n"
                    f"<i>Sharing God's Love All The Way 💜</i>"
                )
                markup = build_theo_group_welcome_keyboard()
            else:
                welcome_text = (
                    f"<b>THEO IS HERE 📖</b>\n\n"
                    f"<blockquote>I am Theo — your Daily Word & Scripture Companion in <b>YouThopiaOS</b>.\n\n"
                    f"I keep our community anchored in God's Word across our 5-bot ecosystem:\n"
                    f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                    f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                    f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                    f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                    f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                    f"<b>⚠️ ADMIN RIGHTS NEEDED</b>\n"
                    f"<blockquote>To send daily 6 AM devotional broadcasts smoothly, please grant Theo <b>Admin Rights</b>!</blockquote>"
                )
                markup = build_theo_member_welcome_keyboard()

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
                logger.warning(f"Failed to send Theo group welcome card: {e}")

        # Case 2: Theo removed or kicked from group
        elif new_status in ("left", "kicked"):
            chat_id = event.chat.id
            group_title = event.chat.title or "your group"
            try:
                await services.chats.set_subscription("theo", chat_id, "daily_devotional", enabled=False)
            except Exception:
                pass

            # Notify Admin in DM
            admin_user_id = event.from_user.id if event.from_user else None
            if admin_user_id:
                try:
                    farewell_text = (
                        f"<b>Theo Departs {group_title} 📖</b>\n\n"
                        f"<blockquote>Theo has been removed from <b>{group_title}</b>.\n"
                        f"Daily devotional broadcasts have been paused for this group. "
                        f"You can re-invite Theo anytime or explore our other 4 community bots below! 💜</blockquote>"
                    )
                    await bot.send_message(
                        chat_id=admin_user_id,
                        text=farewell_text,
                        parse_mode="HTML",
                        reply_markup=build_theo_farewell_keyboard()
                    )
                except Exception as e:
                    logger.warning(f"Could not send Theo farewell DM to admin {admin_user_id}: {e}")

    @router.callback_query(F.data == "theo_prompt_admin")
    async def handle_theo_prompt_admin(callback: CallbackQuery, bot: Bot) -> None:
        await callback.answer()
        instructions = (
            "<b>To Promote Theo to Group Admin:</b>\n\n"
            "1. Open Group Settings ➔ Administrators\n"
            "2. Tap <b>Add Administrator</b> and select <b>@iamtheobot</b>\n"
            "3. Enable Delete Messages & Pin Messages permissions! ⚡"
        )
        try:
            sent_msg = await callback.message.answer(instructions, parse_mode="HTML")
            asyncio.create_task(self_destruct_message(bot, callback.message.chat.id, sent_msg.message_id, 30))
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # ADMIN COMMAND: /leave or /remove_theo
    # -------------------------------------------------------------------------
    @router.message(Command("leave"))
    @router.message(Command("remove_theo"))
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

        try:
            await services.chats.set_subscription("theo", chat_id, "daily_devotional", enabled=False)
        except Exception:
            pass

        # Send DM to admin
        if admin_id:
            try:
                farewell_text = (
                    f"<b>Theo Departs {group_title} 📖</b>\n\n"
                    f"<blockquote>Theo has left <b>{group_title}</b> as requested.\n"
                    f"Daily devotional broadcasts have been paused for this group. "
                    f"You can re-invite Theo anytime or explore our other 4 community bots below! 💜</blockquote>"
                )
                await bot.send_message(
                    chat_id=admin_id,
                    text=farewell_text,
                    parse_mode="HTML",
                    reply_markup=build_theo_farewell_keyboard()
                )
            except Exception as e:
                logger.warning(f"Could not send Theo leave DM to admin {admin_id}: {e}")

        # Leave group cleanly
        try:
            await bot.leave_chat(chat_id)
        except Exception as e:
            logger.warning(f"Theo failed to leave chat {chat_id}: {e}")

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 3: 🌐 Community
    # -------------------------------------------------------------------------
    @router.message(F.text == "🌐 Community")
    @router.message(F.text == "🌐 Community Links")
    async def community_handler(message: Message) -> None:
        if message.chat.type != "private":
            return
        await send_community_exploration_page(message, 1)

    @router.callback_query(F.data == "theo_community_links")
    async def inline_community_links_handler(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            "<b>🌐 YOUTHOPIA BIBLE COMMUNITY LINKS</b>\n"
            "<blockquote>Connect with us across all platforms to stay updated, fellowship, and grow together! 💜</blockquote>",
            parse_mode="HTML",
            reply_markup=get_community_links_keyboard()
        )

    @router.callback_query(F.data.startswith("onboarding_"))
    async def global_onboarding_callback_handler(callback_query: CallbackQuery, services: ServiceContainer) -> None:
        await handle_global_onboarding_callback(callback_query, services)

    @router.callback_query(F.data == "global_ignore")
    async def inline_global_ignore(callback: CallbackQuery) -> None:
        await callback.answer("Threads community link coming soon!", show_alert=True)

    # -------------------------------------------------------------------------
    # BOT-SPECIFIC BUTTON: 🔍 Search Scripture
    # -------------------------------------------------------------------------
    @router.message(F.text == "🔍 Search Scripture")
    @router.callback_query(F.data == "theo_search_scripture")
    async def search_scripture_handler(event: Message | CallbackQuery) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event

        if is_callback:
            await event.answer()

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
    async def subscribe_command(message: Message, bot: Bot, services: ServiceContainer) -> None:
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
                "✅ You are now subscribed to Theo's Daily Verse of the Day. You will receive it daily at 6:00 AM.",
                reply_markup=build_theo_reply_keyboard(),
            )
            return

        try:
            await message.delete()
        except Exception:
            pass

        chat = await register_group_chat(message, services, "theo")
        if not chat:
            return

        try:
            member = await message.chat.get_member(message.from_user.id)
            if member.status not in ("administrator", "creator"):
                msg = await message.answer("❌ Only group admins can subscribe the group to daily verses.")
                asyncio.create_task(self_destruct_message(bot, message.chat.id, msg.message_id, 10))
                return
        except Exception:
            pass

        existing_sub = await services.chats.get_subscription("theo", chat["id"], "daily_devotional")
        if existing_sub and existing_sub.get("enabled"):
            sent_msg = await message.answer(
                f"ℹ️ <b>{message.chat.title}</b> is already subscribed to Theo's Daily Verse (6:00 AM).",
                parse_mode="HTML"
            )
            asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
            return

        await services.chats.set_subscription(
            bot_name="theo",
            chat_id=chat["id"],
            subscription_type="daily_devotional",
            enabled=True,
        )
        sent_msg = await message.answer(
            f"✅ <b>{message.chat.title}</b> is now subscribed to Theo's Daily Verse (6:00 AM).",
            parse_mode="HTML"
        )
        asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))

    @router.message(Command("unsubscribe"))
    async def unsubscribe_command(message: Message, bot: Bot, services: ServiceContainer) -> None:
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

        try:
            await message.delete()
        except Exception:
            pass

        chat = await register_group_chat(message, services, "theo")
        if chat:
            try:
                member = await message.chat.get_member(message.from_user.id)
                if member.status not in ("administrator", "creator"):
                    msg = await message.answer("❌ Only group admins can unsubscribe the group.")
                    asyncio.create_task(self_destruct_message(bot, message.chat.id, msg.message_id, 10))
                    return
            except Exception:
                pass

            await services.chats.set_subscription(
                bot_name="theo",
                chat_id=chat["id"],
                subscription_type="daily_devotional",
                enabled=False,
            )
            sent_msg = await message.answer("⏸️ Paused daily verse delivery for this group.", parse_mode="HTML")
            asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))

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
