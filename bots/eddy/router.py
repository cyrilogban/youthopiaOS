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
    BotCommandScopeChat,
    ChatMemberUpdated,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

from core.telegram_runtime import build_router, register_group_chat, register_chat
from shared.services.container import ServiceContainer
from shared.utils.ui import (
    BOT_FAMILY_DIRECTORY_TEXT,
    get_community_links_keyboard,
    render_shared_profile_card,
    send_community_exploration_page,
    handle_global_onboarding_callback,
)
from bots.eddy.utils.keyboards import (
    build_eddy_reply_keyboard,
    build_eddy_start_inline_keyboard,
    build_eddy_group_welcome_keyboard,
    build_eddy_member_welcome_keyboard,
    build_eddy_farewell_keyboard,
    build_event_card_inline_keyboard,
)


async def self_destruct_message(bot: Bot, chat_id: int, message_id: int, delay_seconds: int = 10) -> None:
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


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
            BotCommand(command="upcomingbirthday", description="View Upcoming Birthdays"),
            BotCommand(command="deletebirthday", description="Delete your registered birthday"),
            BotCommand(command="profile", description="View your profile"),
            BotCommand(command="help", description="Show Ed's instructions"),
        ]

        group_commands = [
            BotCommand(command="calendar", description="View all upcoming events"),
            BotCommand(command="upcomingbirthday", description="View Upcoming Birthdays"),
        ]
        
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

    # -------------------------------------------------------------------------
    # GROUP JOIN WELCOME EVENT (BOT ADDED TO GROUP)
    # -------------------------------------------------------------------------
    @router.my_chat_member()
    async def on_eddy_group_join(event: ChatMemberUpdated, bot: Bot, services: ServiceContainer) -> None:
        old_status = event.old_chat_member.status
        new_status = event.new_chat_member.status

        # Case 1: Eddy added or promoted in group
        if new_status in ("member", "administrator"):
            await register_chat(event.chat, services, "eddy")
            chat_id = event.chat.id
            group_title = event.chat.title or "Group"

            # Status transition: Member -> Admin promotion upgrade
            if old_status == "member" and new_status == "administrator":
                try:
                    sent_msg = await bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"⚡ <b>ADMIN RIGHTS GRANTED!</b>\n\n"
                            f"<blockquote>Thank you for promoting Eddy in <b>{group_title}</b>! "
                            f"Event management, reminders, and birthday celebrations are now fully active. 📅</blockquote>"
                        ),
                        parse_mode="HTML"
                    )
                    asyncio.create_task(self_destruct_message(bot, chat_id, sent_msg.message_id, 5))
                except Exception:
                    pass
                return

            # Differentiated Welcome Card based on Admin vs Member status
            if new_status == "administrator":
                welcome_text = (
                    f"<b>EDDY IS HERE 📅</b>\n\n"
                    f"<blockquote>I am Eddy — your Community Event Manager & Calendar Scheduler in <b>YouThopiaOS</b>.\n\n"
                    f"I keep our community active across our 5-bot ecosystem:\n"
                    f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                    f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                    f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                    f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                    f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                    f"<b>EVENTS QUICK START</b>\n"
                    f"<blockquote>• <b>Weekly Calendar:</b> <code>ACTIVE</code> (Use <code>/calendar</code> anytime).\n"
                    f"• <b>Birthday Shoutouts:</b> <code>ENABLED</code> (Auto-celebrates YouTopians).\n"
                    f"• <b>Admins:</b> Create pop-up events using <code>/new_event</code>.</blockquote>\n\n"
                    f"<i>Sharing God's Love All The Way 💜</i>"
                )
                markup = build_eddy_group_welcome_keyboard()
            else:
                welcome_text = (
                    f"<b>EDDY IS HERE 📅</b>\n\n"
                    f"<blockquote>I am Eddy — your Community Event Manager & Calendar Scheduler in <b>YouThopiaOS</b>.\n\n"
                    f"I keep our community active across our 5-bot ecosystem:\n"
                    f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                    f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                    f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                    f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                    f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                    f"<b>⚠️ ADMIN RIGHTS NEEDED</b>\n"
                    f"<blockquote>To pin event reminders and schedule announcements smoothly, please grant Eddy <b>Admin Rights</b>!</blockquote>"
                )
                markup = build_eddy_member_welcome_keyboard()

            try:
                sent_msg = await bot.send_message(
                    chat_id=chat_id,
                    text=welcome_text,
                    parse_mode="HTML",
                    reply_markup=markup
                )
                # Auto-delete welcome card after 120s
                asyncio.create_task(self_destruct_message(bot, chat_id, sent_msg.message_id, 120))
            except Exception as e:
                logger.warning(f"Failed to send Eddy group welcome card: {e}")

        # Case 2: Eddy removed or kicked from group
        elif new_status in ("left", "kicked"):
            chat_id = event.chat.id
            group_title = event.chat.title or "your group"
            try:
                await services.chats.set_subscription("eddy", chat_id, "events", enabled=False)
            except Exception:
                pass

            # Notify Admin in DM
            admin_user_id = event.from_user.id if event.from_user else None
            if admin_user_id:
                try:
                    farewell_text = (
                        f"<b>Eddy Departs {group_title} 📅</b>\n\n"
                        f"<blockquote>Eddy has been removed from <b>{group_title}</b>.\n"
                        f"Event reminders and birthday broadcasts have been paused for this group. "
                        f"You can re-invite Eddy anytime or explore our other 4 community bots below! 💜</blockquote>"
                    )
                    await bot.send_message(
                        chat_id=admin_user_id,
                        text=farewell_text,
                        parse_mode="HTML",
                        reply_markup=build_eddy_farewell_keyboard()
                    )
                except Exception as e:
                    logger.warning(f"Could not send Eddy farewell DM to admin {admin_user_id}: {e}")

    @router.callback_query(F.data == "eddy_prompt_admin")
    async def handle_eddy_prompt_admin(callback: CallbackQuery, bot: Bot) -> None:
        await callback.answer()
        instructions = (
            "<b>To Promote Eddy to Group Admin:</b>\n\n"
            "1. Open Group Settings ➔ Administrators\n"
            "2. Tap <b>Add Administrator</b> and select <b>@iamedyybot</b>\n"
            "3. Enable Delete Messages & Pin Messages permissions! ⚡"
        )
        try:
            sent_msg = await callback.message.answer(instructions, parse_mode="HTML")
            asyncio.create_task(self_destruct_message(bot, callback.message.chat.id, sent_msg.message_id, 30))
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # ADMIN COMMAND: /leave or /remove_eddy
    # -------------------------------------------------------------------------
    @router.message(Command("leave"))
    @router.message(Command("remove_eddy"))
    async def handle_leave_command(message: Message, bot: Bot, services: ServiceContainer) -> None:
        if message.chat.type == "private":
            await message.answer("⚠️ This command is only for group chats.")
            return

        chat_id = message.chat.id
        group_title = message.chat.title or "your group"
        admin_id = message.from_user.id if message.from_user else None

        # Check if user is admin
        try:
            member = await bot.get_chat_member(chat_id, admin_id)
            if member.status not in ("creator", "administrator"):
                try:
                    await message.delete()
                except Exception:
                    pass
                msg = await message.answer("⚠️ Only group administrators can use /leave.")
                asyncio.create_task(self_destruct_message(bot, chat_id, msg.message_id, 5))
                return
        except Exception:
            pass

        # Send DM to admin
        if admin_id:
            try:
                farewell_text = (
                    f"<b>Eddy Departs {group_title} 📅</b>\n\n"
                    f"<blockquote>Eddy has left <b>{group_title}</b> as requested.\n"
                    f"Event reminders and birthday broadcasts have been paused for this group. "
                    f"You can re-invite Eddy anytime or explore our other 4 community bots below! 💜</blockquote>"
                )
                await bot.send_message(
                    chat_id=admin_id,
                    text=farewell_text,
                    parse_mode="HTML",
                    reply_markup=build_eddy_farewell_keyboard()
                )
            except Exception as e:
                logger.warning(f"Could not send Eddy leave DM to admin {admin_id}: {e}")

        # Leave group cleanly
        try:
            await bot.leave_chat(chat_id)
        except Exception as e:
            logger.warning(f"Eddy failed to leave chat {chat_id}: {e}")

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
                    InlineKeyboardButton(text="📅 View Calendar in DM", url="https://t.me/iamedyybot?start=calendar"),
                    InlineKeyboardButton(text="🎫 My RSVPs", url="https://t.me/iamedyybot?start=events"),
                ]
            ])
            try:
                sent_msg = await message.answer(
                    "<blockquote>📅 <b>Eddy Events Engine is active in this group!</b>\n"
                    "Tap below to open your DM Event Dashboard and view our schedule.</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
            except Exception:
                pass
            return

        await register_group_chat(message, services, "eddy")
        user = await services.identity.resolve_telegram_user(message.from_user)
        first_name = message.from_user.first_name or "Friend"
        user_id = user["id"]

        # Fetch Birthday
        birthday_str = "Not set (Use 🎂 Add Birthday)"
        try:
            state_rec = await services.supabase.find_one_multi("bot_user_state", {"user_id": user_id, "bot_name": "eddy"})
            if state_rec and state_rec.get("state"):
                b_state = state_rec["state"]
                b_month = b_state.get("birthday_month")
                b_day = b_state.get("birthday_day")
                if b_month and b_day:
                    from calendar import month_name
                    birthday_str = f"{month_name[int(b_month)]} {b_day}"
        except Exception:
            pass

        # Fetch RSVPs
        rsvp_count = 0
        try:
            events = await services.events.get_user_upcoming_events(message.from_user.id)
            rsvp_count = len(events) if events else 0
        except Exception:
            pass

        if user.get("engagement_level") == "new":
            welcome_text = (
                f"<b>Welcome to YouThopia Events, {first_name}! 📅</b>\n\n"
                f"<blockquote>I am Eddy (Ed) — event scheduler and community manager in <b>YouThopiaOS</b>.\n\n"
                f"I keep our community active with weekly calendars, live sessions, RSVPs, and birthday celebrations across all 5 pillar bots:\n"
                f"• 📖 <b>Theo:</b> Daily Scripture & Devotionals\n"
                f"• 🎯 <b>Lusy:</b> Quizzes & YouTopian Points (YP)\n"
                f"• 🛡️ <b>Pete:</b> Security & Group Moderation\n"
                f"• 📅 <b>Eddy:</b> Events & Reminders\n"
                f"• 💬 <b>Susy:</b> Welcome & Onboarding</blockquote>\n\n"
                f"<b>SELECT AN OPTION BELOW TO GET STARTED:</b>"
            )
            await services.users.set_engagement_level(user["id"], "active")
        else:
            welcome_text = (
                f"<b>Welcome back, {first_name}! 📅</b>\n\n"
                f"<blockquote>🎂 <b>Registered Birthday:</b> <code>{birthday_str}</code>\n"
                f"🎫 <b>Active Event RSVPs:</b> <code>{rsvp_count} event{'s' if rsvp_count != 1 else ''}</code>\n"
                f"📅 <b>Community Calendar:</b> <code>Updated for this week</code>\n\n"
                f"Never miss a fellowship, live session, or birthday shoutout!</blockquote>\n\n"
                f"<b>WHAT WOULD YOU LIKE TO BE REMINDED OF TODAY?</b>"
            )

        reply_menu = build_eddy_reply_keyboard()
        inline_menu = build_eddy_start_inline_keyboard()

        await message.answer("📅 <b>Welcome to Eddy Events Dashboard!</b>", parse_mode="HTML", reply_markup=reply_menu)
        await message.answer(welcome_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=inline_menu)

    # -------------------------------------------------------------------------
    # GLOBAL BUTTON 1: 👤 My Profile / /profile
    # -------------------------------------------------------------------------
    @router.message(F.text == "👤 My Profile")
    @router.message(Command("profile"))
    @router.callback_query(F.data == "eddy_profile")
    async def profile_handler(event: Message | CallbackQuery, bot: Bot, services: ServiceContainer) -> None:
        is_callback = isinstance(event, CallbackQuery)
        message = event.message if is_callback else event
        user_from = event.from_user

        if is_callback:
            await event.answer()

        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass

            user_first = user_from.first_name if user_from else "Friend"
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="📅 View Profile in DM", url="https://t.me/iamedyybot?start=profile"),
                    InlineKeyboardButton(text="🎫 My RSVPs", url="https://t.me/iamedyybot?start=events"),
                ]
            ])
            try:
                sent_msg = await message.answer(
                    f"<blockquote>👤 <b>{user_first}</b>, your event profile has been sent to your private DM!</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 5))
            except Exception:
                pass

            if user_from:
                try:
                    await send_eddy_profile(message, user_from, services, send_to_dm=True, bot=bot)
                except Exception as e:
                    logger.warning(f"Failed to send Eddy profile to DM: {e}")
            return

        await send_eddy_profile(message, user_from, services)

    async def send_eddy_profile(
        message: Message, from_user: Any, services: ServiceContainer, send_to_dm: bool = False, bot: Bot | None = None
    ) -> None:
        user = await services.identity.resolve_telegram_user(from_user)
        user_id = user["id"]

        birthday_str = "Not set (Use 🎂 Add Birthday)"
        try:
            state_rec = await services.supabase.find_one_multi("bot_user_state", {"user_id": user_id, "bot_name": "eddy"})
            if state_rec and state_rec.get("state"):
                b_state = state_rec["state"]
                b_month = b_state.get("birthday_month")
                b_day = b_state.get("birthday_day")
                if b_month and b_day:
                    from calendar import month_name
                    birthday_str = f"{month_name[int(b_month)]} {b_day}"
        except Exception as e:
            logger.warning(f"Failed to fetch user state for birthday: {e}")

        rsvp_count = 0
        try:
            events = await services.events.get_user_upcoming_events(from_user.id)
            rsvp_count = len(events) if events else 0
        except Exception as e:
            logger.warning(f"Failed to fetch user upcoming events for profile: {e}")

        bot_stats = [
            f"🎂 Birthday: <b>{birthday_str}</b>",
            f"🎫 Event RSVPs: <b>{rsvp_count} event{'s' if rsvp_count != 1 else ''}</b>",
        ]

        card_text = render_shared_profile_card(
            user_data=user,
            telegram_first_name=from_user.first_name or "Friend",
            bot_specific_stats=bot_stats
        )

        if send_to_dm and bot and from_user:
            await bot.send_message(
                chat_id=from_user.id,
                text=card_text,
                parse_mode="HTML",
                reply_markup=build_eddy_reply_keyboard()
            )
        else:
            await message.answer(card_text, parse_mode="HTML", reply_markup=build_eddy_reply_keyboard())

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
                [
                    InlineKeyboardButton(text="📅 Open Eddy Guide in DM", url="https://t.me/iamedyybot?start=help"),
                ]
            ])
            try:
                sent_msg = await message.answer(
                    "<blockquote>📅 <b>Eddy Events Help Guide</b>\n"
                    "Tap below to view full features and calendar options in DM.</blockquote>",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                asyncio.create_task(self_destruct_message(bot, message.chat.id, sent_msg.message_id, 10))
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

    @router.message(Command("upcomingbirthday", "upcomingbirthdays"))
    @router.message(F.text == "🎂 Upcoming Birthdays")
    async def show_upcoming_birthdays(message: Message, services: ServiceContainer) -> None:
        from datetime import datetime, timezone
        from calendar import month_name

        now_utc = datetime.now(timezone.utc)
        current_year = now_utc.year
        today_date = now_utc.date()

        try:
            records = await services.supabase.find_many("bot_user_state", {"bot_name": "eddy"})
        except Exception as e:
            logger.error(f"Failed to fetch bot_user_state for upcoming birthdays: {e}")
            records = []

        upcoming_list = []
        for rec in records:
            state = rec.get("state") or {}
            b_month = state.get("birthday_month")
            b_day = state.get("birthday_day")
            user_id = rec.get("user_id")

            if not (b_month and b_day and user_id):
                continue

            try:
                b_month = int(b_month)
                b_day = int(b_day)

                # Fetch display name
                try:
                    user_rec = await services.supabase.get_by_id("users", user_id)
                    display_name = user_rec.get("display_name") or "YouTopian"
                except Exception:
                    display_name = "YouTopian"

                # Calculate next birthday date in UTC
                try:
                    b_date_this_year = datetime(current_year, b_month, b_day).date()
                except ValueError:
                    b_date_this_year = datetime(current_year, b_month, 28).date()

                if b_date_this_year >= today_date:
                    next_bdate = b_date_this_year
                else:
                    try:
                        next_bdate = datetime(current_year + 1, b_month, b_day).date()
                    except ValueError:
                        next_bdate = datetime(current_year + 1, b_month, 28).date()

                days_until = (next_bdate - today_date).days
                m_short = month_name[b_month][:3]

                upcoming_list.append({
                    "display_name": display_name,
                    "month": b_month,
                    "day": b_day,
                    "month_short": m_short,
                    "days_until": days_until,
                    "next_bdate": next_bdate,
                })
            except Exception:
                continue

        if not upcoming_list:
            await message.answer(
                "<b>🎂 Upcoming Community Birthdays! 🎉</b>\n\n"
                "<i>No registered birthdays found yet.</i>\n\n"
                "💡 Be the first! Register yours with /addbirthday or <b>🎂 Add Birthday</b> button.",
                parse_mode="HTML"
            )
            return

        # Sort chronologically by days_until
        upcoming_list.sort(key=lambda x: x["days_until"])

        this_week = []
        later_this_month = []

        for item in upcoming_list:
            if item["days_until"] == 0:
                day_str = "<b>Today! 🎉</b>"
            elif item["days_until"] == 1:
                day_str = "<b>Tomorrow! 🎈</b>"
            else:
                day_str = f"<b>{item['days_until']} days away</b>"

            entry = f"• <b>{item['display_name']}</b> - {item['month_short']} {item['day']} ({day_str})"

            if item["days_until"] <= 7:
                this_week.append(entry)
            elif item["days_until"] <= 30:
                later_this_month.append(entry)

        lines = ["<b>🎂 Upcoming Community Birthdays! 🎉</b>", "━━━━━━━━━━━━━━━━"]

        if this_week:
            lines.append("<b>🎈 THIS WEEK:</b>")
            lines.extend(this_week)
            lines.append("")

        if later_this_month:
            lines.append("<b>🗓️ LATER THIS MONTH:</b>")
            lines.extend(later_this_month)
            lines.append("")

        if not this_week and not later_this_month:
            lines.append("<b>🗓️ UPCOMING:</b>")
            for item in upcoming_list[:5]:
                if item["days_until"] == 0:
                    day_str = "<b>Today! 🎉</b>"
                elif item["days_until"] == 1:
                    day_str = "<b>Tomorrow! 🎈</b>"
                else:
                    day_str = f"<b>{item['days_until']} days away</b>"
                lines.append(f"• <b>{item['display_name']}</b> - {item['month_short']} {item['day']} ({day_str})")
            lines.append("")

        sent_msg = await message.answer("\n".join(lines), parse_mode="HTML")

        if message.chat.type in {"group", "supergroup"}:
            import asyncio

            async def auto_delete():
                await asyncio.sleep(300)
                try:
                    await sent_msg.delete()
                except Exception:
                    pass
                try:
                    await message.delete()
                except Exception:
                    pass

            asyncio.create_task(auto_delete())

    # ----------------------------------------------------------------------
    # DELETE BIRTHDAY FEATURE
    # ----------------------------------------------------------------------
    @router.message(Command("deletebirthday", "removebirthday"))
    async def prompt_delete_birthday(message: Message, services: ServiceContainer) -> None:
        user = await services.identity.resolve_telegram_user(message.from_user)
        user_id = user["id"]

        try:
            state_rec = await services.supabase.find_one_multi("bot_user_state", {"user_id": user_id, "bot_name": "eddy"})
        except Exception:
            state_rec = None

        state_data = (state_rec.get("state") or {}) if state_rec else {}
        b_month = state_data.get("birthday_month")
        b_day = state_data.get("birthday_day")

        if not (b_month and b_day):
            await message.answer(
                "ℹ️ You don't have a registered birthday saved yet!\n\n"
                "💡 Use /addbirthday or tap <b>🎂 Add Birthday</b> to set yours.",
                parse_mode="HTML"
            )
            return

        from calendar import month_name
        m_name = month_name[int(b_month)]

        text = (
            "<b>🗑️ Delete Registered Birthday</b>\n\n"
            f"Are you sure you want to remove your birthday (<b>{m_name} {b_day}</b>)?\n"
            "You will no longer receive birthday shoutouts or appear in upcoming community birthdays."
        )

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🗑️ Yes, Delete My Birthday", callback_data="eddy_confirm_del_bday"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="eddy_cancel_del_bday")
            ]
        ])

        await message.answer(text, parse_mode="HTML", reply_markup=markup)

    @router.callback_query(F.data == "eddy_confirm_del_bday")
    async def handle_confirm_delete_birthday(callback: CallbackQuery, services: ServiceContainer) -> None:
        user = await services.identity.resolve_telegram_user(callback.from_user)
        user_id = user["id"]

        try:
            state_rec = await services.supabase.find_one_multi("bot_user_state", {"user_id": user_id, "bot_name": "eddy"})
            bot_state = (state_rec.get("state") or {}) if state_rec else {}

            bot_state.pop("birthday_month", None)
            bot_state.pop("birthday_day", None)
            bot_state.pop("birthday_photo_id", None)

            await services.supabase.upsert(
                "bot_user_state",
                {"user_id": user_id, "bot_name": "eddy", "state": bot_state},
                on_conflict="user_id, bot_name"
            )

            await callback.answer("Birthday deleted successfully!")
            await callback.message.edit_text(
                "✅ <b>Birthday Removed</b>\n\n"
                "Your birthday has been removed from Ed's records. You will no longer receive shoutouts or appear in upcoming birthdays.\n\n"
                "💡 <i>You can add it back anytime using /addbirthday!</i>",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to delete birthday for user {user_id}: {e}")
            await callback.answer("An error occurred while deleting your birthday.", show_alert=True)

    @router.callback_query(F.data == "eddy_cancel_del_bday")
    async def handle_cancel_delete_birthday(callback: CallbackQuery) -> None:
        await callback.answer("Deletion cancelled.")
        await callback.message.edit_text(
            "👍 <b>Cancelled.</b> Your registered birthday is safe and remains saved!",
            parse_mode="HTML"
        )

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
