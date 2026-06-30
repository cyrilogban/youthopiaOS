from __future__ import annotations

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    ReplyKeyboardMarkup,
    KeyboardButton,
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

        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="📅 View Calendar"),
                    KeyboardButton(text="🎫 My Events")
                ],
                [
                    KeyboardButton(text="🔔 Reminders"),
                    KeyboardButton(text="About Community")
                ]
            ],
            resize_keyboard=True,
            persistent=True
        )

        sent_msg = await message.answer(welcome_text, parse_mode="HTML", reply_markup=markup)
        
        # Cleanup dashboard in groups to avoid spam
        if message.chat.type != "private":
            import asyncio
            await asyncio.sleep(15)
            try:
                await sent_msg.delete()
            except Exception:
                pass

    @router.message(F.text == "About Community")
    async def on_about_text(message: Message):
        # When they click About Community, we just show the help text
        await handle_help(message)

    @router.callback_query(F.data.startswith("rsvp_"))
    async def handle_event_rsvp(callback: CallbackQuery, services: ServiceContainer):
        # Data format: "rsvp_coming:event_id"
        parts = callback.data.split(":")
        if len(parts) != 2:
            await callback.answer("Error: Invalid event data.", show_alert=True)
            return
            
        action = parts[0].replace("rsvp_", "") # "coming", "maybe", or "no"
        event_id = parts[1]
        user_id = str(callback.from_user.id) # We use Telegram ID for this prototype (would lookup internal UUID in production)
        
        status_map = {
            "coming": "coming",
            "maybe": "maybe",
            "no": "not_attending"
        }
        
        status = status_map.get(action, "registered")
        
        try:
            # Check if this user exists in telegram_accounts, if not they can't RSVP yet.
            # For simplicity, we bypass the full mapping here and just use the Telegram ID in metadata,
            # but ideally we look up their UUID first. We'll pass it to register_participant.
            # Assuming event_service.register_participant handles mapping if we adapt it later.
            # We'll just save it to metadata so it's recorded for now.
            await services.event_service.register_participant(
                event_id=event_id,
                user_id=user_id, # Requires the Supabase User UUID
                status=status,
                metadata={"telegram_id": callback.from_user.id, "first_name": callback.from_user.first_name}
            )
            
            # Flash the success message to the user
            response_map = {
                "coming": "RSVP Saved! ✅ We'll remind you before it starts.",
                "maybe": "RSVP Saved! 🤔 We'll keep you updated.",
                "no": "No problem! ❌ Have a great day."
            }
            
            await callback.answer(response_map.get(action, "RSVP Saved!"), show_alert=False)
            
        except Exception as e:
            # If they don't have an official account yet, they might get a foreign key error
            await callback.answer("Make sure you have started Ed privately first so we know who you are!", show_alert=True)

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
