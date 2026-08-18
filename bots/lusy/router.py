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
    send_community_exploration_page,
    handle_global_onboarding_callback,
)
from bots.lusy.handlers.quizzes import quiz_router
from bots.lusy.utils.keyboards import (
    build_game_selection_inline_keyboard,
    build_lusy_reply_keyboard,
)

logger = logging.getLogger(__name__)


def build_lusy_router(description: str = "Lusy games and XP bot") -> Router:
    router = build_router("lusy", description, include_base_commands=False)
    router.include_router(quiz_router)

    @router.startup()
    async def on_startup(bot: Bot, services: ServiceContainer) -> None:
        import asyncio
        from bots.lusy.services.scheduler import start_auto_game_scheduler
        asyncio.create_task(start_auto_game_scheduler(bot, services))

        private_commands = [
            BotCommand(command="start", description="Open the Game Dashboard"),
            BotCommand(command="playgame", description="Choose and start a Bible game"),
            BotCommand(command="quit", description="Quit active game session"),
            BotCommand(command="leaderboard", description="View global leaderboard"),
            BotCommand(command="yp", description="Check your current YP and Level"),
            BotCommand(command="profile", description="View your profile"),
            BotCommand(command="help", description="How to play and earn YP"),
        ]
        group_commands = [
            BotCommand(command="playgame", description="Choose and start a Bible game"),
            BotCommand(command="autogame", description="Toggle 10-15 daily casual auto games"),
            BotCommand(command="quit", description="Quit active game session"),
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
    async def handle_start(message: Message, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return

        await register_group_chat(message, services, "lusy")
        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"

        welcome_text = (
            f"<b>Think you know the Bible, {first_name}?</b>\n"
            "<blockquote>Prove it. I'm Lusy - and I've got questions that'll test even the sharpest minds. "
            "Answer right, earn YP, rise through the ranks. Let's go! 🎮</blockquote>\n\n"
            "<b>Select a Game Mode Below:</b>"
        )

        inline_markup = build_game_selection_inline_keyboard()
        await message.answer(welcome_text, parse_mode="HTML", reply_markup=inline_markup)

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
    async def help_handler(message: Message) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
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
            "<b>🎮 Lusy | Games & XP Help Guide</b>\n"
            "<blockquote>I am Lusy (@iamlusybot), your quiz master and game host in YOUTHOPIA BIBLE COMMUNITY.\n\n"
            "<b>Lusy Features & Commands</b>\n"
            "• 🎮 <b>Play Games:</b> Test your scripture knowledge with quizzes & challenges.\n"
            "• 🏆 <b>Leaderboard:</b> View the top 10 YouTopians globally.\n"
            "• ⭐ <b>My Points:</b> Check your YP balance, level, and accuracy rate.\n"
            "• <b>/playgame:</b> Choose a game mode directly.\n"
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

    # -------------------------------------------------------------------------
    # BOT-SPECIFIC BUTTON 1: 🎮 Play Games / /playgame
    # -------------------------------------------------------------------------
    @router.message(F.text == "🎮 Play Games")
    @router.message(Command("playgame"))
    @router.callback_query(F.data == "lusy_menu_play")
    async def play_games_handler(event: Message | CallbackQuery) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event

        if is_callback:
            await event.answer()

        markup = build_game_selection_inline_keyboard()
        await message.answer(
            "<b>Choose a Game Mode 🎮</b>\n\n"
            "Select a game mode below to test your scripture knowledge and earn YP!",
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
    async def my_points_handler(message: Message, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return

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
