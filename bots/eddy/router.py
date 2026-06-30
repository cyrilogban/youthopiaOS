from __future__ import annotations

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from core.telegram_runtime import build_router
from shared.services.container import ServiceContainer


def build_eddy_router(description: str) -> Router:
    router = build_router("eddy", description, include_base_commands=False)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        # Define the exact sidebar commands requested
        commands = [
            BotCommand(command="start", description="Open the Main Dashboard"),
            BotCommand(command="help", description="Show Ed's instructions"),
            BotCommand(command="calendar", description="View all upcoming events"),
            BotCommand(command="my_events", description="View events I am attending"),
        ]
        
        # Apply them to DMs and Groups
        await bot.delete_my_commands()
        await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(commands, scope=BotCommandScopeAllGroupChats())

        # Start the background scheduler
        from bots.eddy.services.scheduler import setup_eddy_scheduler
        setup_eddy_scheduler(bot)

    @router.message(Command("start"))
    async def handle_start(message: Message) -> None:
        # Temporary cleanup if in a group
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass

        welcome_text = (
            "<b>Welcome to the YouThopia Operations Center! 📅</b>\n"
            "<blockquote>I am Ed, your community manager. Click a button below to check your schedule!</blockquote>"
        )

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 View Calendar", callback_data="eddy_view_calendar"),
                InlineKeyboardButton(text="🎫 Events I'm Attending", callback_data="eddy_my_rsvps")
            ],
            [
                InlineKeyboardButton(text="🔔 Reminders", callback_data="eddy_reminders"),
                InlineKeyboardButton(text="About the Community", callback_data="eddy_about")
            ]
        ])

        sent_msg = await message.answer(welcome_text, parse_mode="HTML", reply_markup=markup)
        
        # Cleanup dashboard in groups to avoid spam
        if message.chat.type != "private":
            import asyncio
            await asyncio.sleep(15)
            try:
                await sent_msg.delete()
            except Exception:
                pass

    @router.message(Command("help"))
    async def handle_help(message: Message) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
                
        first_name = message.from_user.first_name or "Friend"
        help_text = (
            f"<b>Ed's Help Guide, {first_name}!</b>\n"
            "<blockquote>I'm Ed (@iamedyybot). I am your community manager. I make sure you never miss an event or a Bible study!</blockquote>\n\n"
            "<b>Meet the YouThopia Bot Family</b>\n"
            "<blockquote><b>Theo</b> - <a href=\"https://t.me/iamtheobot\">@iamtheobot</a>\n"
            "Your daily Bible companion. Devotionals, verses, and reflection.\n\n"
            "<b>Lusy</b> - <a href=\"https://t.me/iamlusybot\">@iamlusybot</a>\n"
            "Games, XP, and fun! Earn points and grow your rank.\n\n"
            "<b>Pete</b> - <a href=\"https://t.me/iampetebot\">@iampetebot</a>\n"
            "Security and moderation. Keeping our community safe.\n\n"
            "<b>Susy</b> - <a href=\"https://t.me/iamsusiebot\">@iamsusiebot</a>\n"
            "Your onboarding specialist and guide to the community!</blockquote>\n\n"
            "Sharing God's Love All The Way 💜"
        )
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Join Facebook", url="https://www.facebook.com/share/g/18wG8aWB6t/"),
                InlineKeyboardButton(text="Join Telegram", url="https://t.me/youthopiabiblecommunity"),
            ],
            [
                InlineKeyboardButton(text="Join WhatsApp", url="https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn"),
                InlineKeyboardButton(text="Join Threads", callback_data="ignore"),
            ]
        ])
        
        sent_msg = await message.answer(
            help_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=markup
        )
        
        if message.chat.type != "private":
            import asyncio
            await asyncio.sleep(15)
            try:
                await sent_msg.delete()
            except Exception:
                pass

    @router.callback_query(F.data == "eddy_about")
    async def on_about_callback(callback: CallbackQuery):
        # When they click About Community, we just show the help text
        await handle_help(callback.message)
        await callback.answer()

    return router
