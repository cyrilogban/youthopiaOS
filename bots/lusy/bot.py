from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from core.config import BotConfig
from core.telegram_runtime import build_router, run_polling_bot
from shared.services.container import ServiceContainer


from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from aiogram import Bot

def _router() -> Router:
    router = build_router("lusy", "Lusy games and XP bot", include_base_commands=False)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        commands = [
            BotCommand(command="start", description="Open the Game Dashboard"),
            BotCommand(command="help", description="How to play and earn YP"),
            BotCommand(command="yp", description="Check your current YP and Level"),
        ]
        await bot.delete_my_commands()
        await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(commands, scope=BotCommandScopeAllGroupChats())

    @router.message(Command("start"))
    async def handle_start(message: Message) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass

        welcome_text = (
            "<b>Welcome to the YouThopia Arcade! 🎮</b>\n"
            "<blockquote>I am Lusy, your game master! Ready to earn some YP?</blockquote>"
        )
        
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎮 Play Games"), KeyboardButton(text="🏆 Leaderboard")],
                [KeyboardButton(text="👤 My YP & Stats"), KeyboardButton(text="About Lusy")]
            ],
            resize_keyboard=True,
            persistent=True
        )
        await message.answer(welcome_text, parse_mode="HTML", reply_markup=markup)

    async def handle_help(message: Message) -> None:
        help_text = (
            "<b>ℹ️ About Lusy & Game Rules</b>\n\n"
            "Welcome to the Arcade! Here is how you play:\n"
            "• <b>Play Games</b>: Choose solo or group games to test your knowledge.\n"
            "• <b>My YP & Stats</b>: Track your YouTopian Points and current Level.\n"
            "• <b>Leaderboard</b>: See the Top 10 YouThopians!\n\n"
            "<i>More games are being added soon!</i>"
        )
        await message.answer(help_text, parse_mode="HTML")

    @router.message(Command("help"))
    @router.message(F.text == "About Lusy")
    async def on_help_command(message: Message):
        await handle_help(message)

    @router.message(F.text == "👤 My YP & Stats")
    @router.message(Command("yp"))
    @router.message(Command("xp")) # Keeping /xp just in case someone is used to it
    async def xp(message: Message, services: ServiceContainer) -> None:
        user = await services.identity.resolve_telegram_user(message.from_user)
        level = await services.xp.get_level(user["id"])
        await message.answer(
            f"<b>👤 Your Profile</b>\n\n"
            f"<b>Total YP:</b> {level['total_xp']} ⭐\n"
            f"<b>Current Level:</b> {level['level']} 🏆",
            parse_mode="HTML"
        )

    @router.message(F.text == "🎮 Play Games")
    async def on_play_games(message: Message):
        await message.answer("Games menu is coming soon! 🛠️")

    @router.message(F.text == "🏆 Leaderboard")
    async def on_leaderboard(message: Message):
        await message.answer("Leaderboard is coming soon! 🛠️")

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
