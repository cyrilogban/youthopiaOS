from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from core.config import BotConfig
from core.telegram_runtime import build_router, run_polling_bot
from shared.services.container import ServiceContainer

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot

from bots.lusy.handlers.quizzes import quiz_router


async def render_user_stats(message: Message, telegram_user, services: ServiceContainer) -> None:
    user = await services.identity.resolve_telegram_user(telegram_user)
    user_id = user["id"]
    
    # 1. Fetch level and YP
    level_info = await services.xp.get_level(user_id)
    total_xp = level_info["total_xp"]
    level = level_info["level"]
    
    # Calculate progress bar (10 blocks)
    progress_xp = total_xp % 100
    percentage = progress_xp
    filled_blocks = int(progress_xp // 10)
    empty_blocks = 10 - filled_blocks
    progress_bar = "█" * filled_blocks + "░" * empty_blocks
    
    xp_to_next = 100 - progress_xp
    next_level = level + 1
    
    # Define rank title based on level
    if level < 2:
        title = "Novice"
    elif level < 5:
        title = "Scripture Sage"
    elif level < 10:
        title = "Wisdom Warrior"
    else:
        title = "High Priest"
        
    # 2. Fetch stats from game history
    history = await services.quizzes.get_game_history(user_id)
    total_quizzes = len(history)
    correct_answers = len([h for h in history if h.get("is_correct", False)])
    
    if total_quizzes > 0:
        accuracy = (correct_answers / total_quizzes) * 100
    else:
        accuracy = 0.0
        
    display_name = user.get("display_name") or telegram_user.first_name or "Anonymous"
    
    card_text = (
        f"👤 <b>PLAYER PROFILE: {display_name}</b>\n"
        f"───────────────────────────\n"
        f"🌟 <b>LEVEL {level} ({title})</b>\n"
        f"📈 Progress: <code>[{progress_bar}] {percentage}%</code>\n"
        f"✨ YP Balance: <code>{total_xp} / {level * 100} YP</code>\n"
        f"🎯 ({xp_to_next} YP to Level {next_level})\n\n"
        f"📊 <b>GAME STATISTICS:</b>\n"
        f"├─ Total Quizzes: <code>{total_quizzes} played</code>\n"
        f"├─ Correct Answers: <code>{correct_answers}</code>\n"
        f"└─ Accuracy Rate: <code>{accuracy:.1f}%</code>\n"
        f"───────────────────────────"
    )
    
    await message.answer(card_text, parse_mode="HTML")


def _router() -> Router:
    router = build_router("lusy", "Lusy games and XP bot", include_base_commands=False)
    
    router.include_router(quiz_router)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        private_commands = [
            BotCommand(command="start", description="Open the Game Dashboard"),
            BotCommand(command="quiz", description="Start a Bible Quiz"),
            BotCommand(command="leaderboard", description="View the Top 10 YouTopians!"),
            BotCommand(command="help", description="How to play and earn YP"),
            BotCommand(command="yp", description="Check your current YP and Level"),
        ]
        group_commands = [
            BotCommand(command="quiz", description="Drop a Bible Quiz for the group!"),
            BotCommand(command="leaderboard", description="View the Top 10 YouTopians!"),
            BotCommand(command="help", description="How to play and earn YP"),
        ]
        await bot.delete_my_commands()
        await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())

    @router.message(Command("start"))
    async def handle_start(message: Message) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return

        welcome_text = (
            "<b>Welcome to the YouThopia Bible Quiz!</b>\n"
            "<blockquote>I am Lusy! Think you know the Bible? Let's put your knowledge to the test, learn the Word, and earn some YP!</blockquote>"
        )
        
        inline_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Start Bible Quiz", callback_data="lusy_play_quiz"),
                InlineKeyboardButton(text="Leaderboard", callback_data="lusy_menu_leaderboard")
            ],
            [
                InlineKeyboardButton(text="My YP & Stats", callback_data="lusy_menu_stats"),
                InlineKeyboardButton(text="About Lusy", callback_data="lusy_menu_about")
            ]
        ])
        
        reply_markup = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Start Bible Quiz"), KeyboardButton(text="Leaderboard")],
            [KeyboardButton(text="My YP & Stats"), KeyboardButton(text="About Lusy")]
        ], resize_keyboard=True)
        
        await message.answer(welcome_text, parse_mode="HTML", reply_markup=inline_markup)

    async def handle_help(message: Message) -> None:
        help_text = (
            "<b>About Lusy & Bible Quizzes</b>\n\n"
            "Welcome to the Quiz Room! Here is how it works:\n"
            "• <b>Play Games</b>: Test your Bible knowledge with solo or group quizzes.\n"
            "• <b>My YP & Stats</b>: Track your YouTopian Points and current Level.\n"
            "• <b>Leaderboard</b>: See the Top 10 YouTopians!\n\n"
            "<i>More quizzes and games are being added soon!</i>\n\n"
            "<b>Explore other bots in the community:</b>"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Theo 📖", url="https://t.me/iamtheobot"),
                InlineKeyboardButton(text="Pete 🛡️", url="https://t.me/iampetebot")
            ],
            [
                InlineKeyboardButton(text="Eddy 📅", url="https://t.me/iamedyybot"),
                InlineKeyboardButton(text="Susy 💬", url="https://t.me/iamsusiebot")
            ]
        ])
        await message.answer(help_text, parse_mode="HTML", reply_markup=markup)

    @router.message(Command("help"))
    @router.message(F.text == "About Lusy")
    async def on_help_command(message: Message):
        await handle_help(message)

    @router.message(F.text == "My YP & Stats")
    @router.message(Command("yp"))
    @router.message(Command("xp")) # Keeping /xp just in case someone is used to it
    async def xp(message: Message, services: ServiceContainer) -> None:
        await render_user_stats(message, message.from_user, services)

    @router.message(F.text.in_({"Start Bible Quiz", "Play Games", "🎮 Play Games"}))
    async def on_play_games(message: Message):
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Bible Challenge", callback_data="lusy_play_quiz")]
        ])
        await message.answer(
            "<b>Welcome to the Quiz Arena!</b> Ready to test your knowledge and grow in the Word?\n\n"
            "Choose a quiz mode below to get started:",
            parse_mode="HTML",
            reply_markup=markup
        )

    @router.message(F.text == "Leaderboard")
    @router.message(Command("leaderboard"))
    async def on_leaderboard(message: Message, services: ServiceContainer):
        try:
            users_list = await services.users.get_leaderboard(limit=10)
        except Exception:
            await message.answer("⚠️ Failed to retrieve the leaderboard. Please try again later.")
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
            leaderboard_text += f"{medal} <b>{display_name}</b> (Lvl {level}) — <code>{xp} YP</code>\n"
            
        await message.answer(leaderboard_text, parse_mode="HTML")

    from bots.lusy.handlers.quizzes import on_quiz_command
    @router.message(Command("quiz"))
    @router.message(Command("play"))
    async def handle_quiz_cmd(message: Message, services: ServiceContainer):
        await on_quiz_command(message, services)

    @router.callback_query(F.data == "lusy_menu_play")
    async def on_play_games_callback(callback: CallbackQuery):
        try:
            await on_play_games(callback.message)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error in on_play_games_callback: {e}")
        finally:
            try:
                await callback.answer()
            except Exception:
                pass

    @router.callback_query(F.data == "lusy_menu_leaderboard")
    async def on_leaderboard_callback(callback: CallbackQuery, services: ServiceContainer):
        try:
            await on_leaderboard(callback.message, services)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error in on_leaderboard_callback: {e}")
        finally:
            try:
                await callback.answer()
            except Exception:
                pass

    @router.callback_query(F.data == "lusy_menu_stats")
    async def on_stats_callback(callback: CallbackQuery, services: ServiceContainer):
        try:
            await render_user_stats(callback.message, callback.from_user, services)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error in on_stats_callback: {e}")
        finally:
            try:
                await callback.answer()
            except Exception:
                pass

    @router.callback_query(F.data == "lusy_menu_about")
    async def on_about_callback(callback: CallbackQuery):
        try:
            await handle_help(callback.message)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error in on_about_callback: {e}")
        finally:
            try:
                await callback.answer()
            except Exception:
                pass

    @router.message(lambda message: message.text and "Over to you, @iamlusybot!" in message.text)
    async def respond_to_eddy(message: Message):
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Bible Trivia (Coming Soon)", callback_data="lusy_trivia")],
            [InlineKeyboardButton(text="🔠 Word Scramble (Coming Soon)", callback_data="lusy_scramble")]
        ])
        
        await message.reply(
            "Thanks Ed! 🎤\n\nAlright YouTopians, the weekend is here! What are we playing tonight?",
            reply_markup=markup
        )

    return router


async def run_bot(config: BotConfig, services: ServiceContainer) -> None:
    await run_polling_bot(config, services, description="Lusy games and XP bot", router=_router())
