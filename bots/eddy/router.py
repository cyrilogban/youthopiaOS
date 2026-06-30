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
            "<b>Welcome to the YouThopia Weekly Calendar! 📅</b>\n"
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

    @router.message(Command("calendar"))
    @router.message(F.text == "📅 View Calendar")
    async def on_view_calendar(message: Message, services: ServiceContainer):
        # Fetch upcoming events from the daily schedule dictionary for now
        from bots.eddy.services.scheduler import DAILY_SCHEDULE
        
        cal_text = "<b>📅 This Week's Official Schedule</b>\n\n"
        for day, data in DAILY_SCHEDULE.items():
            cal_text += f"<b>{day}:</b> {data['title']}\n"
            
        cal_text += "\n<i>All events start at 9:00 PM WAT!</i>"
        
        sent_msg = await message.answer(cal_text, parse_mode="HTML")
        
        # In groups, delete the calendar after 30 seconds to avoid spam
        if message.chat.type != "private":
            import asyncio
            await asyncio.sleep(30)
            try:
                await sent_msg.delete()
                await message.delete()
            except Exception:
                pass

    @router.message(Command("my_events"))
    @router.message(F.text == "🎫 My Events")
    async def on_my_events(message: Message, services: ServiceContainer):
        # Placeholder for querying Supabase
        await message.answer(
            "<b>🎫 Your RSVPs</b>\n\n"
            "You are currently RSVP'd to:\n"
            "- <i>No upcoming events found.</i>\n\n"
            "Keep an eye out for Ed's daily announcements at 8:00 PM to secure your spot!",
            parse_mode="HTML"
        )

    @router.message(F.text == "🔔 Reminders")
    async def on_reminders(message: Message):
        # Toggle functionality placeholder
        await message.answer(
            "<b>🔔 Reminder Settings</b>\n\n"
            "Your event reminders are currently: <b>ON</b> ✅\n"
            "I will DM you 1 hour before any event you RSVP to!",
            parse_mode="HTML"
        )

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
        
        # 1. Lookup the official UUID using their Telegram ID
        user_response = services.event_service.db.client.table("telegram_accounts").select("user_id").eq("telegram_id", callback.from_user.id).execute()
        if not user_response.data:
            await callback.answer("Make sure you have started Ed privately first so we know who you are!", show_alert=True)
            return
            
        user_uuid = user_response.data[0]["user_id"]
        
        status_map = {
            "coming": "coming",
            "maybe": "maybe",
            "no": "not_attending"
        }
        
        status = status_map.get(action, "registered")
        
        try:
            await services.event_service.register_participant(
                event_id=event_id,
                user_id=user_uuid,
                status=status,
                metadata={"telegram_id": callback.from_user.id, "first_name": callback.from_user.first_name}
            )
            
            response_map = {
                "coming": "RSVP Saved! ✅ We'll remind you before it starts.",
                "maybe": "RSVP Saved! 🤔 We'll keep you updated.",
                "no": "No problem! ❌ Have a great day."
            }
            
            await callback.answer(response_map.get(action, "RSVP Saved!"), show_alert=False)
            
        except Exception as e:
            await callback.answer("An error occurred while saving your RSVP.", show_alert=True)

    @router.message(Command("my_events"))
    @router.message(F.text == "🎫 My Events")
    async def on_my_events(message: Message, services: ServiceContainer):
        # 1. Lookup the official UUID
        user_response = services.event_service.db.client.table("telegram_accounts").select("user_id").eq("telegram_id", message.from_user.id).execute()
        if not user_response.data:
            await message.answer("I couldn't find your account. Please type /start to register!")
            return
            
        user_uuid = user_response.data[0]["user_id"]
        
        # 2. Get all RSVPs where status is 'coming'
        participant_response = services.event_service.db.client.table("event_participants").select("event_id").eq("user_id", user_uuid).eq("status", "coming").execute()
        
        if not participant_response.data:
            await message.answer(
                "<b>🎫 Your Upcoming RSVPs</b>\n\n"
                "- <i>No upcoming events found.</i>\n\n"
                "Keep an eye out for Ed's daily announcements at 8:00 PM to secure your spot!",
                parse_mode="HTML"
            )
            return
            
        # 3. Get the event details
        event_ids = [p["event_id"] for p in participant_response.data]
        events_response = services.event_service.db.client.table("events").select("title, starts_at").in_("id", event_ids).execute()
        
        events = events_response.data
        if not events:
            await message.answer("You have RSVP'd to events, but they seem to have passed!")
            return
            
        # 4. Format the output
        reply_text = f"<b>🎫 Your Upcoming RSVPs, {message.from_user.first_name}!</b>\n\n"
        for idx, event in enumerate(events, 1):
            # Parse the ISO datetime for nicer formatting (e.g. 2026-06-30T21:00:00 -> 21:00)
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(event["starts_at"])
                time_str = dt.strftime("%I:%M %p")
            except:
                time_str = event["starts_at"]
                
            reply_text += f"{idx}. <b>{event['title']}</b> (at {time_str})\n"
            
        reply_text += "\n<i>I will send you a DM reminder 1 hour before these start!</i>"
        
        await message.answer(reply_text, parse_mode="HTML")

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
