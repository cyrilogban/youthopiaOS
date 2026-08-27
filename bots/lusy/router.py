from __future__ import annotations

import logging
from typing import Any

from aiogram import F, Router, Bot
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
    handle_group_profile_acknowledgment,
)
from bots.lusy.handlers.quizzes import quiz_router, self_destruct_message
from bots.lusy.utils.keyboards import (
    build_game_selection_inline_keyboard,
    build_lusy_reply_keyboard,
    build_lusy_group_welcome_keyboard,
    build_lusy_member_welcome_keyboard,
    build_lusy_farewell_keyboard,
)

logger = logging.getLogger(__name__)


def build_lusy_router(description: str = "Lusy games and XP bot") -> Router:
    router = Router(name="lusy_root")
    router.include_router(quiz_router)

    base_router = build_router("lusy", description, include_base_commands=False)
    router.include_router(base_router)

    @router.startup()
    async def on_startup(bot: Bot, services: ServiceContainer) -> None:
        import asyncio
        from bots.lusy.services.scheduler import start_auto_quiz_scheduler
        asyncio.create_task(start_auto_quiz_scheduler(bot, services))

        private_commands = [
            BotCommand(command="start", description="Open the Quiz Dashboard"),
            BotCommand(command="playquiz", description="Choose and start a Bible quiz"),
            BotCommand(command="quit", description="Quit active quiz session"),
            BotCommand(command="leaderboard", description="View global leaderboard"),
            BotCommand(command="yp", description="Check your current YP and Level"),
            BotCommand(command="profile", description="View your profile"),
            BotCommand(command="help", description="How to play and earn YP"),
        ]
        group_commands = [
            BotCommand(command="playquiz", description="Choose and start a Bible quiz"),
            BotCommand(command="autoquiz", description="Check Auto Quiz status"),
            BotCommand(command="autoquiz_on", description="Enable 10-15 daily casual quizzes"),
            BotCommand(command="autoquiz_off", description="Disable daily casual quizzes"),
            BotCommand(command="quit", description="Quit active quiz session"),
            BotCommand(command="leaderboard", description="View global leaderboard"),
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
                [
                    InlineKeyboardButton(text="🚀 Open Private Dashboard", url="https://t.me/iamlusybot?start=dashboard"),
                    InlineKeyboardButton(text="🎯 Play Group Quiz", callback_data="lusy_menu_play"),
                ]
            ])
            try:
                sent_msg = await message.answer(
                    "<blockquote>🎯 <b>Lusy Quiz Engine is active in this group!</b>\n"
                    "Type <b>/playquiz</b> to launch a round, or tap below to open your DM Dashboard.</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                import asyncio
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
            except Exception:
                pass
            return

        await register_group_chat(message, services, "lusy")
        user = await services.identity.resolve_telegram_user(message.from_user)
        user_id = user["id"]
        first_name = message.from_user.first_name or "Friend"

        # Check if user is returning by checking game history
        try:
            history = await services.quizzes.get_game_history(user_id)
        except Exception:
            history = []

        total_quizzes = len(history)

        if total_quizzes > 0:
            try:
                level_info = await services.xp.get_level(user_id)
                total_xp = level_info.get("total_xp", 0)
                level = level_info.get("level", 1)
            except Exception:
                total_xp = user.get("total_xp", 0)
                level = user.get("level", 1)

            rank_title = "Novice" if level < 2 else ("Scripture Sage" if level < 5 else ("Wisdom Warrior" if level < 10 else "High Priest"))
            correct_answers = len([h for h in history if h.get("is_correct", False)])
            accuracy = (correct_answers / total_quizzes * 100) if total_quizzes > 0 else 0.0

            welcome_text = (
                f"<b>Welcome back, {first_name}! 🎯</b>\n\n"
                f"<blockquote>🌟 <b>Level {level} ({rank_title})</b> | <code>{total_xp} YP</code>\n"
                f"🎯 <b>Accuracy:</b> <code>{accuracy:.1f}%</code> ({correct_answers}/{total_quizzes} played)\n\n"
                "Ready to take on another challenge and advance your rank?</blockquote>\n\n"
                "<b>SELECT A QUIZ MODE BELOW:</b>"
            )
        else:
            welcome_text = (
                f"<b>Welcome to Scripture Mastery, {first_name}! 🎯</b>\n\n"
                "<blockquote>I am Lusy — your Scripture Mastery & Gamification Engine in <b>YouThopiaOS</b>.\n\n"
                "Here in our community, mastering God's Word is an exciting journey we share together! Test your knowledge, earn <b>YouTopian Points (YP)</b>, and climb our global leaderboard synced across all 5 YouThopiaOS pillar bots:\n"
                "• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                "• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                "• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                "• 📅 <b>Eddy:</b> Events & Reminders\n"
                "• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                "<b>SELECT A QUIZ MODE BELOW:</b>"
            )

        reply_markup = build_lusy_reply_keyboard()
        inline_markup = build_game_selection_inline_keyboard()
        await message.answer("🎯 <b>Welcome to Lusy Quiz Dashboard!</b>", parse_mode="HTML", reply_markup=reply_markup)
        await message.answer(welcome_text, parse_mode="HTML", reply_markup=inline_markup)

    # -------------------------------------------------------------------------
    # GROUP JOIN WELCOME EVENT (BOT ADDED TO GROUP)
    # -------------------------------------------------------------------------
    @router.my_chat_member()
    async def on_lusy_group_join(event: ChatMemberUpdated, bot: Bot, services: ServiceContainer) -> None:
        old_status = event.old_chat_member.status
        new_status = event.new_chat_member.status

        # 1. Trigger welcome card when Lusy is added or promoted in a group
        if new_status in ("member", "administrator"):
            try:
                await register_chat(event.chat, services, "lusy")
            except Exception as e:
                logger.warning(f"Failed to register group chat for Lusy on join: {e}")

            # Status transition: Member -> Admin promotion upgrade
            if old_status == "member" and new_status == "administrator":
                try:
                    sent_msg = await bot.send_message(
                        chat_id=event.chat.id,
                        text="<blockquote>⚡ <b>ADMIN RIGHTS GRANTED!</b> Lusy is now fully empowered as a Group Administrator. All quiz features unlocked!</blockquote>",
                        parse_mode="HTML"
                    )
                    import asyncio
                    asyncio.create_task(self_destruct_message(bot, event.chat.id, sent_msg.message_id, 5))
                except Exception as e:
                    logger.error(f"Failed to post Lusy admin promotion confirmation: {e}")
                return

            try:
                is_member_only = (new_status == "member")

                admin_note = (
                    "\n\n⚠️ <b>ADMIN RIGHTS NEEDED:</b> I was added as a regular member. "
                    "To allow me to delete expired trigger messages, pin quiz leaderboards, and run Auto Quizzes cleanly, "
                    "please promote me to <b>Group Administrator</b>!"
                    if is_member_only else ""
                )

                welcome_card = (
                    "<b>LUSY IS HERE</b>\n\n"
                    "<blockquote>I am Lusy — your Scripture Mastery & Quiz Engine in <b>YouThopiaOS</b>.\n\n"
                    "Every quiz answered here earns <b>YouTopian Points (YP)</b>, advancing your global rank across our entire 5-bot ecosystem:\n"
                    "• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                    "• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                    "• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                    "• 📅 <b>Eddy:</b> Events & Reminders\n"
                    "• 💬 <b>Susy:</b> Welcome & Onboarding"
                    f"{admin_note}</blockquote>\n\n"
                    "<b>GROUP QUICK START</b>\n"
                    "<blockquote>• <b>/playquiz</b> — Launch an instant Bible Quiz round.\n"
                    "• <b>Auto Quiz:</b> <code>ENABLED</code> (10–15 casual drops daily).\n"
                    "• <b>Admins:</b> Manage anytime using <code>/autoquiz_on</code> or <code>/autoquiz_off</code>.</blockquote>\n\n"
                    "<i>Sharing God's Love All The Way 💜</i>"
                )

                markup = build_lusy_member_welcome_keyboard() if is_member_only else build_lusy_group_welcome_keyboard()
                sent_msg = await bot.send_message(
                    chat_id=event.chat.id,
                    text=welcome_card,
                    parse_mode="HTML",
                    reply_markup=markup
                )
                import asyncio
                asyncio.create_task(self_destruct_message(bot, event.chat.id, sent_msg.message_id, 120))
            except Exception as e:
                logger.error(f"Failed to post Lusy group welcome card: {e}")

        # 2. Trigger DM farewell notification when Lusy is removed/kicked from a group
        elif new_status in ("left", "kicked"):
            try:
                chat = await register_chat(event.chat, services, "lusy")
                if chat:
                    await services.chats.mark_bot_status("lusy", chat["id"], new_status, enabled=False)

                if event.from_user:
                    admin_name = event.from_user.first_name or "Friend"
                    group_title = event.chat.title or "your group"
                    dm_farewell_text = (
                        "<b>FAREWELL FROM LUSY</b>\n\n"
                        f"<blockquote>Hi <b>{admin_name}</b>, Lusy has been removed from <b>{group_title}</b>.\n\n"
                        "Thank you for having me! All player <b>YouTopian Points (YP)</b> earned by your members remain safely saved in <b>YouThopiaOS</b>.</blockquote>\n\n"
                        "<b>DISCOVER OTHER YOUTHOPIAOS BOTS</b>\n"
                        "<blockquote>You can still explore or invite our sister bots anytime:\n"
                        "• 📖 <b>Theo (@iamtheobot):</b> Daily Scripture & Devotionals\n"
                        "• 🛡️ <b>Pete (@iampetebot):</b> Security & Group Moderation\n"
                        "• 📅 <b>Eddy (@iamedyybot):</b> Events & Reminders\n"
                        "• 💬 <b>Susy (@iamsusiebot):</b> Welcome & Onboarding</blockquote>\n\n"
                        "<i>God Bless You & See You Soon! 💜</i>"
                    )
                    markup = build_lusy_farewell_keyboard()
                    await bot.send_message(
                        chat_id=event.from_user.id,
                        text=dm_farewell_text,
                        parse_mode="HTML",
                        reply_markup=markup
                    )
            except Exception as e:
                logger.error(f"Failed to handle Lusy group removal event: {e}")

    # -------------------------------------------------------------------------
    # ADMIN COMMAND: /leave or /remove_lusy (Graceful Group Departure)
    # -------------------------------------------------------------------------
    @router.message(Command("leave"))
    @router.message(Command("remove_lusy"))
    async def leave_group_handler(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type == "private":
            await message.answer("This command is used to remove Lusy from a group chat.")
            return

        is_admin = False
        import os
        admin_ids_str = os.getenv("ADMIN_OWNER_ID") or os.getenv("ADMIN_IDS") or ""
        admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]
        if message.from_user and message.from_user.id in admin_ids:
            is_admin = True
        else:
            try:
                member = await bot.get_chat_member(message.chat.id, message.from_user.id)
                if member.status in ("administrator", "creator"):
                    is_admin = True
            except Exception:
                pass

        if not is_admin:
            await message.answer("<blockquote>Only group administrators can request Lusy to leave the group.</blockquote>", parse_mode="HTML")
            return

        group_title = message.chat.title or "this group"
        markup = build_lusy_farewell_keyboard()

        if message.from_user:
            try:
                admin_name = message.from_user.first_name or "Friend"
                dm_farewell_text = (
                    "<b>FAREWELL FROM LUSY</b>\n\n"
                    f"<blockquote>Hi <b>{admin_name}</b>, Lusy has left <b>{group_title}</b> as requested.\n\n"
                    "Thank you for having me! All player <b>YouTopian Points (YP)</b> earned by your members remain safely saved in <b>YouThopiaOS</b>.</blockquote>\n\n"
                    "<b>DISCOVER OTHER YOUTHOPIAOS BOTS</b>\n"
                    "<blockquote>You can still explore or invite our sister bots anytime:\n"
                    "• 📖 <b>Theo (@iamtheobot):</b> Daily Scripture & Devotionals\n"
                    "• 🛡️ <b>Pete (@iampetebot):</b> Security & Group Moderation\n"
                    "• 📅 <b>Eddy (@iamedyybot):</b> Events & Reminders\n"
                    "• 💬 <b>Susy (@iamsusiebot):</b> Welcome & Onboarding</blockquote>\n\n"
                    "<i>God Bless You & See You Soon! 💜</i>"
                )
                await bot.send_message(message.from_user.id, dm_farewell_text, parse_mode="HTML", reply_markup=markup)
            except Exception:
                pass

        try:
            chat = await register_chat(message.chat, services, "lusy")
            if chat:
                await services.chats.mark_bot_status("lusy", chat["id"], "left", enabled=False)
            await bot.leave_chat(message.chat.id)
        except Exception as e:
            logger.error(f"Failed to execute Lusy leave_chat: {e}")

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 1: 👤 My Profile / /profile
    # -------------------------------------------------------------------------
    @router.message(F.text == "👤 My Profile")
    @router.message(Command("profile"))
    async def profile_handler(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            await handle_group_profile_acknowledgment(message, bot)
            # Send profile directly to user's private DM
            try:
                user_first = message.from_user.first_name if message.from_user else "Friend"
                user = await services.identity.resolve_telegram_user(message.from_user)
                level_info = await services.xp.get_level(user["id"])
                total_xp = level_info["total_xp"]
                level = level_info["level"]
                rank_title = "Novice" if level < 2 else ("Scripture Sage" if level < 5 else ("Wisdom Warrior" if level < 10 else "High Priest"))
                history = await services.quizzes.get_game_history(user["id"])
                total_quizzes = len(history)
                correct_answers = len([h for h in history if h.get("is_correct", False)])
                accuracy = (correct_answers / total_quizzes * 100) if total_quizzes > 0 else 0.0
                bot_stats = [
                    f"🎮 Rank: <b>{rank_title}</b>",
                    f"🎯 Accuracy: <b>{accuracy:.1f}%</b> ({correct_answers}/{total_quizzes} played)",
                ]
                card_text = render_shared_profile_card(
                    user_data=user,
                    telegram_first_name=user_first,
                    bot_specific_stats=bot_stats
                )
                await bot.send_message(message.from_user.id, card_text, parse_mode="HTML", reply_markup=build_lusy_reply_keyboard())
            except Exception as e:
                logger.warning(f"Failed to send Lusy profile to DM: {e}")
            return

        await send_lusy_profile(message, services)

    @router.callback_query(F.data == "lusy_menu_stats")
    async def inline_profile_handler(callback: CallbackQuery, services: ServiceContainer) -> None:
        if callback.message.chat.type != "private":
            await callback.answer("Please check your points in DM!", show_alert=True)
            return
        await callback.answer()
        await send_lusy_profile(callback.message, services, telegram_user=callback.from_user)

    async def send_lusy_profile(
        message: Message, services: ServiceContainer, telegram_user: Any | None = None
    ) -> None:
        user_from = telegram_user or message.from_user
        user = await services.identity.resolve_telegram_user(user_from)
        user_id = user["id"]

        # Fetch level and YP
        level_info = await services.xp.get_level(user_id)
        total_xp = level_info["total_xp"]
        level = level_info["level"]

        # Define rank title based on level
        if level < 2:
            rank_title = "Novice"
        elif level < 5:
            rank_title = "Scripture Sage"
        elif level < 10:
            rank_title = "Wisdom Warrior"
        else:
            rank_title = "High Priest"

        # Fetch game history statistics
        history = await services.quizzes.get_game_history(user_id)
        total_quizzes = len(history)
        correct_answers = len([h for h in history if h.get("is_correct", False)])
        accuracy = (correct_answers / total_quizzes * 100) if total_quizzes > 0 else 0.0

        # Lusy-specific stats for profile card
        bot_stats = [
            f"🎮 Rank: <b>{rank_title}</b>",
            f"🎯 Accuracy: <b>{accuracy:.1f}%</b> ({correct_answers}/{total_quizzes} played)",
        ]

        card_text = render_shared_profile_card(
            user_data=user,
            telegram_first_name=user_from.first_name or "Friend",
            bot_specific_stats=bot_stats
        )

        await message.answer(
            card_text,
            parse_mode="HTML",
            reply_markup=build_lusy_reply_keyboard()
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
                [InlineKeyboardButton(text="📖 Open Lusy Guide in DM", url="https://t.me/iamlusybot?start=help")]
            ])
            try:
                sent_msg = await message.answer(
                    "<blockquote>📖 <b>Looking for Lusy Help?</b> Tap below to view your full guide in private.</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                import asyncio
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
            except Exception:
                pass
            return

        await send_lusy_help(message)

    @router.callback_query(F.data == "lusy_menu_about")
    async def inline_help_handler(callback: CallbackQuery) -> None:
        if callback.message.chat.type != "private":
            await callback.answer("Please view help in DM!", show_alert=True)
            return
        await callback.answer()
        await send_lusy_help(callback.message)

    async def send_lusy_help(message: Message) -> None:
        help_text = (
            "<b>🎯 Lusy | Quizzes & XP Help Guide</b>\n"
            "<blockquote>I am Lusy (@iamlusybot), your quiz master in YOUTHOPIA BIBLE COMMUNITY.\n\n"
            "<b>Lusy Features & Commands</b>\n"
            "• 🎯 <b>Play Quizzes:</b> Test your scripture knowledge with quizzes & challenges.\n"
            "• 🏆 <b>Leaderboard:</b> View the top 10 YouTopians globally.\n"
            "• ⭐ <b>My Points:</b> Check your YP balance, level, and accuracy rate.\n"
            "• <b>/playquiz:</b> Choose a quiz mode directly.\n"
            "• <b>/yp or /xp:</b> View your player profile and level progress.</blockquote>\n\n"
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
    # GLOBAL BUTTON 3: 🌐 Community
    # -------------------------------------------------------------------------
    @router.message(F.text == "🌐 Community")
    @router.message(F.text == "🌐 Community Links")
    async def community_handler(message: Message) -> None:
        if message.chat.type != "private":
            return
        await send_community_exploration_page(message, 1)

    @router.callback_query(F.data.startswith("onboarding_"))
    async def global_onboarding_callback_handler(callback_query: CallbackQuery, services: ServiceContainer) -> None:
        await handle_global_onboarding_callback(callback_query, services)

    @router.callback_query(F.data == "lusy_menu_directory")
    async def inline_directory_handler(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(
            BOT_FAMILY_DIRECTORY_TEXT,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=get_community_links_keyboard(),
        )

    @router.callback_query(F.data == "lusy_prompt_admin")
    async def inline_prompt_admin_handler(callback: CallbackQuery, bot: Bot) -> None:
        try:
            member = await bot.get_chat_member(callback.message.chat.id, callback.from_user.id)
            if member.status not in ("administrator", "creator"):
                await callback.answer("⚠️ Only group administrators can promote bots to admin!", show_alert=True)
                return
        except Exception:
            pass

        await callback.answer()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Open Admin Permission Sheet", url="https://t.me/iamlusybot?startgroup=admin&admin=delete_messages+pin_messages+invite_users")]
        ])
        sent_msg = await callback.message.answer(
            "<blockquote>🎯 <b>Lusy Administrator Setup</b>\n\n"
            "Tap below to open Telegram's permission sheet with required rights pre-checked!</blockquote>",
            parse_mode="HTML",
            reply_markup=markup
        )
        import asyncio
        asyncio.create_task(self_destruct_message(bot, callback.message.chat.id, sent_msg.message_id, 20))

    # -------------------------------------------------------------------------
    # BOT-SPECIFIC BUTTON 1: 🎯 Play Quizzes / /playquiz
    # -------------------------------------------------------------------------
    @router.message(F.text.in_({"🎯 Play Quizzes", "🎮 Play Games"}))
    @router.message(Command("playquiz", "playgame"))
    @router.callback_query(F.data == "lusy_menu_play")
    async def play_games_handler(event: Message | CallbackQuery) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event

        if is_callback:
            await event.answer()

        markup = build_game_selection_inline_keyboard()
        await message.answer(
            "<b>Choose a Quiz Mode 🎯</b>\n\n"
            "Select a quiz mode below to test your scripture knowledge and earn YP!",
            parse_mode="HTML",
            reply_markup=markup
        )

    # -------------------------------------------------------------------------
    # BOT-SPECIFIC BUTTON 2: 🏆 Leaderboard / /leaderboard
    # -------------------------------------------------------------------------
    @router.message(F.text == "🏆 Leaderboard")
    @router.message(Command("leaderboard"))
    async def leaderboard_handler(message: Message, services: ServiceContainer) -> None:
        await send_lusy_leaderboard(message, services)

    @router.callback_query(F.data == "lusy_menu_leaderboard")
    async def inline_leaderboard_handler(callback: CallbackQuery, services: ServiceContainer) -> None:
        await callback.answer()
        await send_lusy_leaderboard(callback.message, services)

    async def send_lusy_leaderboard(message: Message, services: ServiceContainer) -> None:
        try:
            users_list = await services.users.get_leaderboard(limit=10)
        except Exception as e:
            logger.error(f"Failed to fetch leaderboard: {e}")
            await message.answer("⚠️ Failed to retrieve leaderboard. Please try again later.")
            return

        if not users_list:
            await message.answer("No scores recorded yet. Be the first to play and earn YP!")
            return

        leaderboard_text = "<b>🏆 Top YouTopians (Global Leaderboard)</b>\n\n"
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for idx, user in enumerate(users_list):
            display_name = user.get("display_name") or "Anonymous"
            xp = user.get("total_xp", 0)
            level = user.get("level", 1)
            medal = medals[idx] if idx < len(medals) else f"#{idx+1}"
            leaderboard_text += f"{medal} <b>{display_name}</b> (Lvl {level}) - <code>{xp} YP</code>\n"

        await message.answer(
            leaderboard_text,
            parse_mode="HTML",
            reply_markup=build_lusy_reply_keyboard()
        )

    # -------------------------------------------------------------------------
    # BOT-SPECIFIC BUTTON 3: ⭐ My Points / /yp / /xp
    # -------------------------------------------------------------------------
    @router.message(F.text == "⭐ My Points")
    @router.message(Command("yp"))
    @router.message(Command("xp"))
    async def my_points_handler(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass

            user_first = message.from_user.first_name if message.from_user else "Friend"
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 View Player Profile in DM", url="https://t.me/iamlusybot?start=profile")]
            ])
            try:
                sent_msg = await message.answer(
                    f"<blockquote>👤 <b>{user_first}</b>, your player stats have been sent to your private DM!</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                import asyncio
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 5))
            except Exception:
                pass

        user = await services.identity.resolve_telegram_user(message.from_user)
        user_id = user["id"]

        level_info = await services.xp.get_level(user_id)
        total_xp = level_info["total_xp"]
        level = level_info["level"]

        progress_xp = total_xp % 100
        percentage = progress_xp
        filled_blocks = int(progress_xp // 10)
        empty_blocks = 10 - filled_blocks
        progress_bar = "█" * filled_blocks + "░" * empty_blocks

        xp_to_next = 100 - progress_xp
        next_level = level + 1

        if level < 2:
            rank_title = "Novice"
        elif level < 5:
            rank_title = "Scripture Sage"
        elif level < 10:
            rank_title = "Wisdom Warrior"
        else:
            rank_title = "High Priest"

        history = await services.quizzes.get_game_history(user_id)
        total_quizzes = len(history)
        correct_answers = len([h for h in history if h.get("is_correct", False)])
        accuracy = (correct_answers / total_quizzes * 100) if total_quizzes > 0 else 0.0

        display_name = user.get("display_name") or message.from_user.first_name or "Anonymous"

        card_text = (
            f"👤 <b>PLAYER STATS: {display_name}</b>\n"
            f"───────────────────────────\n"
            f"🌟 <b>LEVEL {level} ({rank_title})</b>\n"
            f"📈 Progress: <code>[{progress_bar}] {percentage}%</code>\n"
            f"✨ YP Balance: <code>{total_xp} YP</code>\n"
            f"🎯 (Need {xp_to_next} YP to reach Level {next_level})\n\n"
            f"📊 <b>GAME STATISTICS:</b>\n"
            f"• Total Quizzes: <code>{total_quizzes} played</code>\n"
            f"• Correct Answers: <code>{correct_answers}</code>\n"
            f"• Accuracy Rate: <code>{accuracy:.1f}%</code>\n"
            f"───────────────────────────"
        )

        if message.chat.type != "private":
            try:
                await bot.send_message(message.from_user.id, card_text, parse_mode="HTML", reply_markup=build_lusy_reply_keyboard())
            except Exception:
                pass
        else:
            await message.answer(card_text, parse_mode="HTML", reply_markup=build_lusy_reply_keyboard())

    # -------------------------------------------------------------------------
    # EDDY TO LUSY HANDOFF LISTENER
    # -------------------------------------------------------------------------
    @router.message(lambda message: message.text and "Over to you, @iamlusybot!" in message.text)
    async def respond_to_eddy(message: Message) -> None:
        markup = build_game_selection_inline_keyboard()
        await message.reply(
            "Thanks Ed! 🎤\n\nAlright YouTopians, the weekend is here! What game are we playing tonight?",
            reply_markup=markup
        )

    return router
