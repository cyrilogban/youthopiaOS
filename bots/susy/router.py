from __future__ import annotations

import asyncio
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from core.router_builder import build_router
from shared.services.container import ServiceContainer

# Will add Susy's official photo URL here when available
SUSY_PHOTO = None

def build_susy_router(description: str) -> Router:
    router = build_router("susy", description, include_base_commands=False)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        # Define the exact sidebar commands requested
        commands = [
            BotCommand(command="start", description="Wake Up Susy"),
            BotCommand(command="help", description="Show help information"),
        ]
        
        # Apply them to DMs and Groups
        await bot.delete_my_commands()
        await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(commands, scope=BotCommandScopeAllGroupChats())

    @router.message(Command("start"))
    async def handle_start(message: Message, services: ServiceContainer) -> None:
        # Group Cleanup Mechanism
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
                
        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"
        
        welcome_text = (
            f"<b>Welcome to YOUTHOPIA BIBLE COMMUNITY, {first_name}! 🤍</b>\n"
            "<blockquote>I am Susy, your first friend and guide here in the YouThopia ecosystem.\n\n"
            "We are a Gen Z Christian community built to help you grow in your faith, connect with believers, and have fun doing it!</blockquote>\n\n"
            "<b>Getting Started</b>\n"
            "<blockquote>I'm here to show you around! If you are new here, my job is to make sure you know exactly how everything works.\n\n"
            "Whenever you feel lost, just ask me for help!</blockquote>\n\n"
            "Sharing God's Love All The Way. 💜"
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
        
        if SUSY_PHOTO:
            sent_msg = await message.answer_photo(
                photo=SUSY_PHOTO,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            sent_msg = await message.answer(
                welcome_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup
            )
            
        # Delete Susy's welcome message in groups after 15s to prevent spam
        if message.chat.type != "private":
            await asyncio.sleep(15)
            try:
                await sent_msg.delete()
            except Exception:
                pass

    @router.message(Command("help"))
    async def handle_help(message: Message, services: ServiceContainer) -> None:
        # Group Cleanup Mechanism
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
                
        first_name = message.from_user.first_name or "Friend"
        help_text = (
            f"<b>Susy's Help Guide, {first_name}!</b>\n"
            "<blockquote>I'm Susy (@iamsusiebot). I am your onboarding specialist and guide to the community!</blockquote>\n\n"
            "<b>Meet the YouThopia Bot Family</b>\n"
            "<blockquote><b>Theo</b> - <a href=\"https://t.me/iamtheobot\">@iamtheobot</a>\n"
            "Your daily Bible companion. Devotionals, verses, and reflection.\n\n"
            "<b>Lusy</b> - <a href=\"https://t.me/iamlusybot\">@iamlusybot</a>\n"
            "Games, XP, and fun! Earn points and grow your rank.\n\n"
            "<b>Pete</b> - <a href=\"https://t.me/iampetebot\">@iampetebot</a>\n"
            "Security and moderation. Keeping our community safe.\n\n"
            "<b>Ed</b> - <a href=\"https://t.me/iamedyybot\">@iamedyybot</a>\n"
            "Events and announcements. Never miss what is happening.</blockquote>\n\n"
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
            await asyncio.sleep(15)
            try:
                await sent_msg.delete()
            except Exception:
                pass

    return router
