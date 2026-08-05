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
    CallbackQuery,
    BotCommandScopeChat
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import logging

logger = logging.getLogger(__name__)

from core.telegram_runtime import build_router
from shared.services.container import ServiceContainer
from shared.utils.ui import (
    BOT_FAMILY_DIRECTORY_TEXT,
    get_community_links_keyboard,
    render_shared_profile_card,
)
from bots.eddy.utils.keyboards import (
    build_eddy_reply_keyboard,
    build_event_card_inline_keyboard,
)


class EventCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_time = State()
    waiting_for_description = State()
    waiting_for_broadcast = State()

class AddBirthday(StatesGroup):
    waiting_for_date = State()
    waiting_for_photo = State()

def build_eddy_router(description: str) -> Router:
    router = build_router("eddy", description, include_base_commands=False)

    @router.startup()
    async def on_startup(bot: Bot) -> None:
        # Define sidebar commands for DMs per spec
        private_commands = [
            BotCommand(command="start", description="Open Ed main dashboard"),
            BotCommand(command="calendar", description="View this week's event schedule"),
            BotCommand(command="my_events", description="View events I am attending"),
            BotCommand(command="addbirthday", description="Add your birthday"),
            BotCommand(command="profile", description="View your profile"),
            BotCommand(command="help", description="Show Ed's instructions"),
        ]

        group_commands = [
            BotCommand(command="calendar", description="View all upcoming events"),
        ]
        
        try:
            await bot.delete_my_commands()
        except Exception:
            pass
        await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())

        # Admin commands registration
        admin_ids_str = os.getenv("ADMIN_OWNER_ID") or os.getenv("ADMIN_IDS")
        if admin_ids_str:
            admin_ids = [aid.strip() for aid in admin_ids_str.split(",") if aid.strip().isdigit()]
            admin_commands = private_commands + [
                BotCommand(command="new_event", description="[Admin] Create a pop-up event")
            ]
            for admin_id in admin_ids:
                try:
                    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=int(admin_id)))
                except Exception as e:
                    logger.error(f"Failed to set admin commands for {admin_id}: {e}")

        # Start background scheduler
        from bots.eddy.services.scheduler import setup_eddy_scheduler
        setup_eddy_scheduler(bot)

    @router.message(Command("start"))
    async def handle_start(message: Message, services: ServiceContainer) -> None:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            return
            
        try:
            await services.identity.resolve_telegram_user(message.from_user)
        except Exception as e:
            logger.error(f"Failed to register user in Ed /start: {e}")

        first_name = message.from_user.first_name or "Friend"
        welcome_text = (
            f"<b>Welcome to the YouThopia Weekly Calendar, {first_name}! 📅</b>\n"
            "<blockquote>I am Ed (Eddy), your community manager and event scheduler.\n\n"
            "Use the menu below to view upcoming events, check your RSVPs, or register your birthday!</blockquote>"
        )

        markup = build_eddy_reply_keyboard()
        await message.answer(welcome_text, parse_mode="HTML", reply_markup=markup)

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
        await send_eddy_profile(message, services)

    async def send_eddy_profile(message: Message, services: ServiceContainer) -> None:
        user = await services.identity.resolve_telegram_user(message.from_user)
        user_id = user["id"]

        # Fetch birthday if registered
        profile_rec = await services.supabase.find_one_multi("user_profiles", {"user_id": user_id})
        birthday_str = "Not set (Use 🎂 Add Birthday)"
        if profile_rec and profile_rec.get("birthday"):
            birthday_str = profile_rec["birthday"]

        # Fetch RSVPs count
        rsvps = await services.supabase.find_many("event_rsvps", {"user_id": user_id})
        rsvp_count = len(rsvps) if rsvps else 0

        # Ed-specific stats for profile card
        bot_stats = [
            f"🎂 Birthday: <b>{birthday_str}</b>",
            f"🎫 Event RSVPs: <b>{rsvp_count} events</b>",
        ]

        card_text = render_shared_profile_card(
            user_data=user,
            telegram_first_name=message.from_user.first_name or "Friend",
            bot_specific_stats=bot_stats
        )

        await message.answer(card_text, parse_mode="HTML", reply_markup=build_eddy_reply_keyboard())

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
        await send_eddy_help(message)

    async def send_eddy_help(message: Message) -> None:
        help_text = (
            "<b>📅 Ed | Events Bot Help Guide</b>\n"
            "<blockquote>I am Ed (@iamedyybot), your event scheduler and community manager in YOUTHOPIA BIBLE COMMUNITY.\n\n"
            "<b>Ed Features & Commands</b>\n"
            "• 📅 <b>View Calendar:</b> Check this week's official community events.\n"
            "• 🎫 <b>My Events:</b> View events you have RSVP'd for.\n"
            "• 🎂 <b>Add Birthday:</b> Register your birthday for community shoutouts.\n"
            "• 🔔 <b>Reminders:</b> Toggle event notifications.\n"
            "• <b>/calendar:</b> Display weekly schedule in DM or group.\n"
            "• <b>/my_events:</b> List your RSVPs.\n"
            "• <b>/addbirthday:</b> Register your birthday date.</blockquote>\n\n"
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
    # GLOBAL BUTTON 3: 🌐 Community Links
    # -------------------------------------------------------------------------
    @router.message(F.text == "🌐 Community Links")
    async def community_links_handler(message: Message) -> None:
        if message.chat.type != "private":
            return
        await message.answer(
            "<b>🌐 YOUTHOPIA BIBLE COMMUNITY LINKS</b>\n"
            "<blockquote>Connect with us across all platforms to stay updated, fellowship, and grow together! 💜</blockquote>",
            parse_mode="HTML",
            reply_markup=get_community_links_keyboard()
        )


    @router.message(Command("calendar"))
    @router.message(F.text == "📅 View Calendar")
    async def on_view_calendar(message: Message, services: ServiceContainer):
        if message.chat.type != "private" and message.text == "📅 View Calendar":
            return
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


    @router.message(F.text == "🔔 Reminders")
    async def on_reminders(message: Message, services: ServiceContainer):
        if message.chat.type != "private":
            return
        try:
            # 1. Resolve the official User UUID
            user = await services.identity.resolve_telegram_user(message.from_user)
            user_id = user["id"]
            
            # 2. Fetch current bot state
            state_record = await services.supabase.find_one_multi("bot_user_state", {"user_id": user_id, "bot_name": "eddy"})
            
            state = {}
            if state_record:
                state = state_record.get("state") or {}
                
            # Default is True if not set
            current_status = state.get("reminders_enabled", True)
            
            # 3. Toggle the status
            new_status = not current_status
            state["reminders_enabled"] = new_status
            
            # 4. Save back to Supabase
            await services.supabase.upsert(
                "bot_user_state", 
                {"user_id": user_id, "bot_name": "eddy", "state": state},
                on_conflict="user_id, bot_name"
            )
            
            # 5. Tell the user
            status_text = "<b>ON</b> ✅" if new_status else "<b>OFF</b> 🔕"
            explanation = (
                "I will DM you 15 minutes before any event you RSVP to!" 
                if new_status 
                else "I will no longer send you automated event DMs. You will need to check the group!"
            )
            
            await message.answer(
                f"<b>🔔 Reminder Settings Updated!</b>\n\n"
                f"Your event reminders are now: {status_text}\n\n"
                f"<i>{explanation}</i>",
                parse_mode="HTML"
            )
        except Exception as e:
            await message.answer(f"Whoops! Something went wrong trying to update your settings: {e}")

    @router.message(F.text == "About Community")
    async def on_about_text(message: Message):
        if message.chat.type != "private":
            return
        # When they click About Community, we just show the help text
        await handle_help(message)

    @router.callback_query(F.data.startswith("rsvp_"))
    async def handle_event_rsvp(callback: CallbackQuery, services: ServiceContainer, bot: Bot):
        # Data format: "rsvp_coming:event_id"
        parts = callback.data.split(":")
        if len(parts) != 2:
            await callback.answer("Error: Invalid event data.", show_alert=True)
            return
            
        action = parts[0].replace("rsvp_", "") # "coming", "maybe", or "no"
        event_id = parts[1]
        
        # 1. Check if the event has passed
        event = await services.events.get_event_by_id(event_id)
        if not event:
            await callback.answer("Error: Event not found.", show_alert=True)
            return
            
        from datetime import datetime
        from zoneinfo import ZoneInfo
        event_time = datetime.fromisoformat(event["starts_at"])
        now_wat = datetime.now(ZoneInfo("Africa/Lagos"))
        
        event_has_passed = now_wat > event_time

        # 2. Lookup the official UUID using their Telegram ID
        user = await services.users.get_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Please start me privately first!", show_alert=False)
            me = await bot.get_me()
            link = f"https://t.me/{me.username}?start=rsvp"
            
            if event_has_passed:
                warning_text = (
                    f"Hey <a href='tg://user?id={callback.from_user.id}'>{callback.from_user.first_name}</a>! "
                    f"This event has already passed! ⏰\n\n"
                    f"Also, you haven't introduced yourself to me yet. "
                    f"👉 <a href='{link}'>Click here to start me privately</a> so you don't miss the next one!"
                )
            else:
                warning_text = (
                    f"Hey <a href='tg://user?id={callback.from_user.id}'>{callback.from_user.first_name}</a>! "
                    f"I need to know who you are before you can RSVP.\n\n"
                    f"👉 <a href='{link}'>Click here to Start Ed Privately</a>"
                )
                
            warn_msg = await callback.message.answer(
                warning_text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            # Cleanup warning message after 20 seconds so it doesn't clutter
            import asyncio
            async def delete_later():
                await asyncio.sleep(20)
                try:
                    await warn_msg.delete()
                except Exception:
                    pass
            asyncio.create_task(delete_later())
            return

        if event_has_passed:
            await callback.answer("Oops! This event has already finished. ❌", show_alert=True)
            return
            
        user_uuid = user["id"]
        
        status_map = {
            "coming": "coming",
            "no": "not_attending"
        }
        
        status = status_map.get(action, "registered")
        
        try:
            await services.events.register_participant(
                event_id=event_id,
                user_id=user_uuid,
                status=status,
                metadata={"telegram_id": callback.from_user.id, "first_name": callback.from_user.first_name}
            )
            
            response_map = {
                "coming": "RSVP Saved! ✅ We'll remind you before it starts.",
                "no": "No problem! ❌ Have a great day."
            }
            
            await callback.answer(response_map.get(action, "RSVP Saved!"), show_alert=False)
            
        except Exception as e:
            await callback.answer("An error occurred while saving your RSVP.", show_alert=True)

    @router.message(Command("my_events", "myevents"))
    @router.message(F.text == "🎫 My Events")
    async def on_my_events(message: Message, services: ServiceContainer):
        if message.chat.type != "private":
            return
        events = await services.events.get_user_upcoming_events(message.from_user.id)
        if events is None:
            await message.answer("I couldn't find your account. Please type /start to register!")
            return
            
        if not events:
            await message.answer(
                "<b>🎫 Your Upcoming RSVPs</b>\n\n"
                "- <i>No upcoming events found.</i>\n\n"
                "Keep an eye out for Ed's daily announcements at 8:00 PM to secure your spot!",
                parse_mode="HTML"
            )
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
    async def handle_help_command(message: Message) -> None:
        if message.chat.type != "private":
            return
        await handle_help(message)

    async def handle_help(message: Message) -> None:
        if message.chat.type != "private":
            return
            
        first_name = message.from_user.first_name or "Friend"
        help_text = (
            f"<b>Ed's Help Guide, {first_name}!</b>\n"
            "<blockquote>I'm Ed (@iamedyybot). I am your community manager. I make sure you never miss an event or a Bible study!</blockquote>\n\n"
            "<b>Meet the YouThopia Bot Family</b>\n"
            "<blockquote><b>Theo</b> - <a href=\"https://t.me/iamtheobot\">@iamtheobot</a>\n"
            "Your daily Bible companion. Devotionals, verses, and reflection.\n\n"
            "<b>Lusy</b> - <a href=\"https://t.me/iamlusybot\">@iamlusybot</a>\n"
            "Games, YP, and fun! Earn points and grow your rank.\n\n"
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
        
        await message.answer(
            help_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=markup
        )


    @router.callback_query(F.data == "eddy_about")
    async def on_about_callback(callback: CallbackQuery):
        # When they click About Community, we just show the help text
        await handle_help(callback.message)
        await callback.answer()

    # ----------------------------------------------------------------------
    # MILESTONE 4: AD-HOC ADMIN EVENT CREATOR (FSM)
    # ----------------------------------------------------------------------
    def is_admin(user_id: int) -> bool:
        admin_ids_str = os.getenv("ADMIN_OWNER_ID") or os.getenv("ADMIN_IDS", "")
        admin_ids = [aid.strip() for aid in admin_ids_str.split(",") if aid.strip()]
        return str(user_id) in admin_ids

    @router.message(Command("new_event"))
    async def start_event_creation(message: Message, state: FSMContext):
        if message.chat.type != "private":
            await message.delete()
            try:
                await message.bot.send_message(message.from_user.id, "Let's keep event creation in our private DM! Type /new_event here.")
            except Exception:
                pass
            return
            
        if not is_admin(message.from_user.id):
            return # Silent ignore for non-admins
            
        await state.set_state(EventCreation.waiting_for_title)
        await message.answer("Let's create a custom event! 🛠️\n\nFirst, what is the <b>Title</b> of the event?", parse_mode="HTML")

    @router.message(EventCreation.waiting_for_title)
    async def process_title(message: Message, state: FSMContext):
        await state.update_data(title=message.text)
        await state.set_state(EventCreation.waiting_for_time)
        await message.answer(f"Great title! ({message.text})\n\nNow, what <b>Date and Time</b> is this happening?\n<i>(e.g., 'Tomorrow at 10:00 AM' or 'July 15th at 4 PM WAT')</i>", parse_mode="HTML")

    @router.message(EventCreation.waiting_for_time)
    async def process_time(message: Message, state: FSMContext):
        await state.update_data(starts_at=message.text)
        await state.set_state(EventCreation.waiting_for_description)
        await message.answer("Got it! Finally, give me a short <b>Description</b> for this event.", parse_mode="HTML")

    @router.message(EventCreation.waiting_for_description)
    async def process_description(message: Message, state: FSMContext, services: ServiceContainer):
        await state.update_data(description=message.text)
        data = await state.get_data()
        
        # We will save it directly using EventService
        try:
            # We will use the starts_at string directly for now, or map it.
            # In a true prod app, we'd parse this to ISO datetime. Here we'll just save it as the description header.
            from datetime import datetime
            
            event_payload = {
                "title": data["title"],
                "description": f"🕒 {data['starts_at']}\n\n{data['description']}",
                "starts_at": datetime.now().isoformat(), # Dummy ISO for DB constraint
                "status": "scheduled"
            }
            
            created_event = await services.events.create_event(event_payload)
            event_id = created_event[0]["id"] if isinstance(created_event, list) else created_event["id"]
            
            await state.update_data(event_id=event_id)
            await state.set_state(EventCreation.waiting_for_broadcast)
            
            markup = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📢 Yes, Broadcast It!")],
                    [KeyboardButton(text="🤫 No, just save it")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            
            await message.answer("<b>Event Saved to Supabase! ✅</b>\n\nDo you want me to broadcast this to the Main Group right now?", parse_mode="HTML", reply_markup=markup)
            
        except Exception as e:
            await message.answer(f"Error saving to DB: {e}")
            await state.clear()

    @router.message(EventCreation.waiting_for_broadcast)
    async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
        data = await state.get_data()
        event_id = data.get("event_id")
        
        if message.text == "📢 Yes, Broadcast It!":
            main_group_id = os.getenv("MAIN_GROUP_ID")
            if not main_group_id:
                await message.answer("MAIN_GROUP_ID not set in .env! Cannot broadcast.")
            else:
                announcement = (
                    f"<b>🚨 SPECIAL ANNOUNCEMENT 🚨</b>\n\n"
                    f"<b>Event:</b> {data['title']}\n"
                    f"<blockquote>{data['description']}</blockquote>\n\n"
                    "Can you make it?"
                )
                
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Yes", callback_data=f"rsvp_coming:{event_id}"),
                        InlineKeyboardButton(text="Maybe", callback_data=f"rsvp_maybe:{event_id}"),
                        InlineKeyboardButton(text="No", callback_data=f"rsvp_no:{event_id}")
                    ]
                ])
                
                try:
                    await bot.send_message(chat_id=main_group_id, text=announcement, parse_mode="HTML", reply_markup=markup)
                    await message.answer("Broadcast sent successfully to the Main Group! 🚀", reply_markup=ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton(text="📅 View Calendar"), KeyboardButton(text="🎫 My Events")], [KeyboardButton(text="🔔 Reminders"), KeyboardButton(text="About Community")]],
                        resize_keyboard=True, persistent=True
                    ))
                except Exception as e:
                    await message.answer(f"Failed to broadcast: {e}")
        else:
            await message.answer("Okay, event saved silently! 🤫", reply_markup=ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton(text="📅 View Calendar"), KeyboardButton(text="🎫 My Events")], [KeyboardButton(text="🔔 Reminders"), KeyboardButton(text="About Community")]],
                        resize_keyboard=True, persistent=True
                    ))
            
        await state.clear()

    # ------------------------------------------------------------------
    # BIRTHDAY FEATURE
    # ------------------------------------------------------------------

    @router.message(Command("addbirthday"))
    @router.message(F.text == "🎂 Add Birthday")
    async def start_add_birthday(message: Message, state: FSMContext):
        if message.chat.type != "private":
            return
        await state.set_state(AddBirthday.waiting_for_date)
        await message.answer(
            "Yay! 🎂 I love birthdays!\n\n"
            "When is your special day? Please reply with your birth date.\n"
            "*(Format: DD/MM or just type the month and day, e.g. July 6)*",
            parse_mode="Markdown"
        )

    @router.message(AddBirthday.waiting_for_date)
    async def process_birthday_date(message: Message, state: FSMContext):
        import re
        from datetime import datetime
        
        text = message.text.strip().lower()
        b_month = None
        b_day = None
        
        # Try DD/MM or MM/DD parsing
        match = re.search(r'(\d{1,2})[/-](\d{1,2})', text)
        if match:
            part1 = int(match.group(1))
            part2 = int(match.group(2))
            
            # Simple heuristic: if part2 > 12, it must be the day
            if part2 > 12:
                b_month = part1
                b_day = part2
            elif part1 > 12:
                b_month = part2
                b_day = part1
            else:
                # Ambiguous, assume DD/MM for Nigeria/UK style
                b_day = part1
                b_month = part2
        else:
            # Try parsing natural language like "July 6"
            months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
            for i, m in enumerate(months):
                if m in text:
                    b_month = i + 1
                    break
            
            # Find the day number
            day_match = re.search(r'\b(\d{1,2})(st|nd|rd|th)?\b', text)
            if day_match:
                b_day = int(day_match.group(1))
                
        if not b_month or not b_day or b_month < 1 or b_month > 12 or b_day < 1 or b_day > 31:
            await message.answer("Oops! I couldn't quite understand that date. 😅\nPlease try again using the format **DD/MM** (e.g., 06/07 for July 6th).", parse_mode="Markdown")
            return
            
        await state.update_data(b_month=b_month, b_day=b_day)
        await state.set_state(AddBirthday.waiting_for_photo)
        
        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Skip")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        await message.answer(
            f"Got it! 📸\n\n"
            f"Would you like me to include a cool photo of you in your birthday shoutout?\n"
            f"If yes, please send me an image right now. If no, just click **Skip**!",
            parse_mode="Markdown",
            reply_markup=markup
        )

    @router.message(AddBirthday.waiting_for_photo)
    async def process_birthday_photo(message: Message, state: FSMContext, services: ServiceContainer):
        photo_id = None
        
        if message.photo:
            photo_id = message.photo[-1].file_id
        elif message.text and message.text.lower() == "skip":
            photo_id = None
        else:
            await message.answer(
                "Oops! That looks like text. 😅\n\n"
                "Please send me an actual photo to use for your birthday shoutout, or just type/click **Skip** if you don't want a photo!"
            )
            return
            
        data = await state.get_data()
        b_month = data.get("b_month")
        b_day = data.get("b_day")
        
        try:
            # 1. Resolve user ID
            user = await services.identity.resolve_telegram_user(message.from_user)
            user_id = user["id"]
            
            # 2. Fetch existing state
            state_record = await services.supabase.find_one_multi("bot_user_state", {"user_id": user_id, "bot_name": "eddy"})
            bot_state = {}
            if state_record:
                bot_state = state_record.get("state") or {}
                
            # 3. Update state
            bot_state["birthday_month"] = b_month
            bot_state["birthday_day"] = b_day
            bot_state["birthday_photo_id"] = photo_id
            
            await services.supabase.upsert(
                "bot_user_state", 
                {"user_id": user_id, "bot_name": "eddy", "state": bot_state},
                on_conflict="user_id, bot_name"
            )
            
            # Return their normal keyboard
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📅 View Calendar"), KeyboardButton(text="🎫 My Events")],
                    [KeyboardButton(text="🎂 Add Birthday"), KeyboardButton(text="🔔 Reminders")],
                    [KeyboardButton(text="About Community")]
                ],
                resize_keyboard=True,
                persistent=True
            )
            
            await message.answer(
                "🎉 **All set!**\n\nI have saved your birthday. Get ready for a massive shoutout when your special day arrives! 🎈",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await message.answer("Oh no, something went wrong while saving your birthday. Please try again later!")
            
        await state.clear()

    # ----------------------------------------------------------------------
    # CHANNEL-TO-TOPIC MIRROR (YouThopia Channel -> Group Topic Thread)
    # ----------------------------------------------------------------------
    @router.channel_post()
    async def mirror_channel_post(message: Message, bot: Bot):
        """
        Fires whenever a new post appears in the linked channel (@joinyouthopia).
        Copies it into the General topic of the Main Group and attaches a button linking back.
        """
        logger.info(f"📢 CHANNEL POST DETECTED in Eddy! Msg ID: {message.message_id}, Chat: {message.chat.title} ({message.chat.id})")
        
        main_group_id_str = os.getenv("MAIN_GROUP_ID", "-1001904672000")
        try:
            main_group_id = int(main_group_id_str)
        except ValueError:
            logger.error(f"Invalid MAIN_GROUP_ID: {main_group_id_str}")
            return

        topic_id_str = os.getenv("ANNOUNCEMENTS_TOPIC_ID", "1")
        topic_id = int(topic_id_str) if topic_id_str.isdigit() else None
        channel_username = os.getenv("CHANNEL_USERNAME", "joinyouthopia").replace("@", "").strip()

        channel_link = f"https://t.me/{channel_username}/{message.message_id}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💜 View in Channel 💜", url=channel_link)]
            ]
        )

        # Attempt 1: Copy with explicit topic ID
        try:
            kwargs = {
                "chat_id": main_group_id,
                "from_chat_id": message.chat.id,
                "message_id": message.message_id,
                "reply_markup": keyboard,
            }
            if topic_id:
                kwargs["message_thread_id"] = topic_id

            await bot.copy_message(**kwargs)
            logger.info(f"Eddy successfully mirrored channel post {message.message_id} to group {main_group_id} topic {topic_id}")
            return
        except Exception as e:
            logger.warning(f"Eddy topic copy attempt failed with topic_id={topic_id}: {e}")

        # Attempt 2: Fallback copy without message_thread_id (for General topic)
        try:
            await bot.copy_message(
                chat_id=main_group_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=keyboard,
            )
            logger.info(f"Eddy successfully mirrored channel post {message.message_id} to main group {main_group_id} (fallback without thread_id)")
            return
        except Exception as fallback_err:
            logger.warning(f"Eddy fallback copy failed for channel post {message.message_id}: {fallback_err}")

        # Attempt 3: Fallback forward_message (for Polls, Quizzes, and uncopyable Telegram types)
        try:
            fwd_kwargs = {
                "chat_id": main_group_id,
                "from_chat_id": message.chat.id,
                "message_id": message.message_id,
            }
            if topic_id:
                fwd_kwargs["message_thread_id"] = topic_id

            await bot.forward_message(**fwd_kwargs)
            logger.info(f"Eddy successfully forwarded channel post {message.message_id} to main group {main_group_id} topic {topic_id}")
        except Exception as fwd_err:
            logger.error(f"Eddy forward fallback also failed for channel post {message.message_id}: {fwd_err}")

    return router
