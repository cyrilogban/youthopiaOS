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

def _router() -> Router:
    router = build_router("lusy", "Lusy games and XP bot", include_base_commands=False)
    
    router.include_router(quiz_router)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        private_commands = [
            BotCommand(command="start", description="Open the Game Dashboard"),
            BotCommand(command="quiz", description="Start a Bible Quiz"),
            BotCommand(command="help", description="How to play and earn YP"),
            BotCommand(command="yp", description="Check your current YP and Level"),
        ]
        group_commands = [
            BotCommand(command="quiz", description="Drop a Bible Quiz for the group!"),
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
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Play Games", callback_data="lusy_menu_play"),
                InlineKeyboardButton(text="Leaderboard", callback_data="lusy_menu_leaderboard")
            ],
            [
                InlineKeyboardButton(text="My YP & Stats", callback_data="lusy_menu_stats"),
                InlineKeyboardButton(text="About Lusy", callback_data="lusy_menu_about")
            ]
        ])
        await message.answer(welcome_text, parse_mode="HTML", reply_markup=markup)

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
        user = await services.identity.resolve_telegram_user(message.from_user)
        level = await services.xp.get_level(user["id"])
        await message.answer(
            f"<b>Your Profile</b>\n\n"
            f"<b>Total YP:</b> {level['total_xp']}\n"
            f"<b>Current Level:</b> {level['level']}",
            parse_mode="HTML"
        )

    @router.message(F.text.in_({"Play Games", "🎮 Play Games"}))
    async def on_play_games(message: Message):
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Bible Quiz", callback_data="lusy_play_quiz")]
        ])
        await message.answer("<b>Choose a Game Mode!</b>\nWhat would you like to play today?", parse_mode="HTML", reply_markup=markup)

    @router.message(F.text == "Leaderboard")
    async def on_leaderboard(message: Message):
        await message.answer("Leaderboard is coming soon!")

    @router.callback_query(F.data == "lusy_menu_play")
    async def on_play_games_callback(callback: CallbackQuery):
        await callback.answer()
        await on_play_games(callback.message)

    @router.callback_query(F.data == "lusy_menu_leaderboard")
    async def on_leaderboard_callback(callback: CallbackQuery):
        await callback.answer()
        await on_leaderboard(callback.message)

    @router.callback_query(F.data == "lusy_menu_stats")
    async def on_stats_callback(callback: CallbackQuery, services: ServiceContainer):
        await callback.answer()
        user = await services.identity.resolve_telegram_user(callback.from_user)
        level = await services.xp.get_level(user["id"])
        await callback.message.answer(
            f"<b>Your Profile</b>\n\n"
            f"<b>Total YP:</b> {level['total_xp']}\n"
            f"<b>Current Level:</b> {level['level']}",
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "lusy_menu_about")
    async def on_about_callback(callback: CallbackQuery):
        await callback.answer()
        await handle_help(callback.message)

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
