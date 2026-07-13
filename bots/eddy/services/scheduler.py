from __future__ import annotations

import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shared.services.event_service import EventService
from shared.services.user_service import UserService
from core.config import BotConfig

logger = logging.getLogger(__name__)

# The weekly schedule logic
DAILY_SCHEDULE = {
    "Monday": {
        "title": "Motivational Monday",
        "description": "Kickstart the week with practical tips for growth hacking and personal development strategies."
    },
    "Tuesday": {
        "title": "Discussion Tuesday",
        "description": "Turbocharge Tuesday with epic Bible study lessons, live group calls, and deep-dive Scripture discussions!"
    },
    "Wednesday": {
        "title": "Wisdom Wednesday",
        "description": "Power up Wednesday with hard-hitting debunking of tough biblical questions, deep doctrine dives, and expert-level insights!"
    },
    "Thursday": {
        "title": "Throwback Thursday",
        "description": "Revisiting old posts, testimonies, or past impactful discussions from the community to reflect and gain new insights."
    },
    "Friday": {
        "title": "Fun Friday",
        "description": "Lighthearted engagement with clean, faith-based memes, fun polls, or interactive games like 'Finish this Bible verse...'."
    },
    "Saturday": {
        "title": "Prayer & Reflection",
        "description": "A moment to pause, reflect, and pray. A space for sharing prayers, reflections, and requests to support one another."
    },
    "Sunday": {
        "title": "Community Hangout",
        "description": "A time for live discussions, Q&A sessions, or virtual hangouts. A chance to connect, share insights, and grow together."
    }
}

from shared.db.supabase import SupabaseGateway
import os
from zoneinfo import ZoneInfo

WAT_TZ = ZoneInfo("Africa/Lagos")

async def post_daily_announcement(bot: Bot, group_chat_id: int):
    """Runs every day at 5:00 PM WAT to announce the 9:00 PM event."""
    now_wat = datetime.now(WAT_TZ)
    today_name = now_wat.strftime("%A")
    event_data = DAILY_SCHEDULE.get(today_name)
    
    if not event_data:
        return
        
    title = event_data["title"]
    description = event_data["description"]
        
    # Check for Last Wednesday of the Month Book Review
    if today_name == "Wednesday":
        from datetime import timedelta
        # Logic: If adding 7 days pushes us into the next month, this is the last Wednesday
        if (now_wat + timedelta(days=7)).month != now_wat.month:
            title = "Wisdom Wednesday (Monthly Book Review!)"
            description = "It's the last Wednesday of the month! Join us for our deep-dive Monthly Book review."

    # Initialize Supabase and EventService
    supabase = SupabaseGateway(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
    event_service = EventService(supabase)
    
    # 0. Delete yesterday's announcement to keep the group clean
    try:
        latest_event = await event_service.get_latest_event()
        if latest_event and latest_event.get("metadata", {}).get("announcement_message_id"):
            old_msg_id = latest_event["metadata"]["announcement_message_id"]
            try:
                await bot.delete_message(group_chat_id, old_msg_id)
            except Exception as e:
                logger.error(f"Could not delete old 5PM announcement: {e}")
    except Exception as e:
        logger.error(f"Error checking for old announcement: {e}")

    # 1. Create the event in the database
    event_starts_at = now_wat.replace(hour=21, minute=0, second=0, microsecond=0)
    event_payload = {
        "title": title,
        "description": description,
        "starts_at": event_starts_at.isoformat(),
        "status": "scheduled"
    }
    
    try:
        created_event = await event_service.create_event(event_payload)
        event_id = created_event[0]["id"] if isinstance(created_event, list) else created_event["id"]
    except Exception as e:
        logger.error(f"Failed to create event in Supabase: {e}")
        return

    # 2. Format the message
    announcement = (
        f"<b>Happy {today_name}, YouTopians!</b> 🚀\n\n"
        f"<b>Tonight's Event:</b> {title}\n"
        f"<blockquote>{description}</blockquote>\n\n"
        "We are starting tonight at 9:00 PM WAT. Can you make it?"
    )
    
    # 3. Attach the specific event_id to the callback data
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Yes", callback_data=f"rsvp_coming:{event_id}"),
            InlineKeyboardButton(text="No", callback_data=f"rsvp_no:{event_id}")
        ]
    ])
    
    try:
        sent_msg = await bot.send_message(group_chat_id, announcement, parse_mode="HTML", reply_markup=markup)
        
        # 4. Save the message ID so we can delete it tomorrow
        event_metadata = {"announcement_message_id": sent_msg.message_id}
        await event_service.update_event(event_id, {"metadata": event_metadata})
    except Exception as e:
        logger.error(f"Failed to send 5PM announcement: {e}")

async def send_group_reminder(bot: Bot, group_chat_id: int):
    """Runs every day at 8:00 PM WAT to remind the group."""
    now_wat = datetime.now(WAT_TZ)
    today_name = now_wat.strftime("%A")
    event_data = DAILY_SCHEDULE.get(today_name)
    
    if not event_data:
        return
        
    title = event_data["title"]
    if today_name == "Wednesday":
        from datetime import timedelta
        if (now_wat + timedelta(days=7)).month != now_wat.month:
            title = "Wisdom Wednesday (Monthly Book Review!)"

    reminder_text = (
        f"⏰ <b>Reminder!</b>\n\n"
        f"<b>{title}</b> is starting in exactly 1 hour in this group. Grab your notes and get ready! 🚀"
    )
    
    try:
        await bot.send_message(group_chat_id, reminder_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to send 8PM group reminder: {e}")


async def send_event_reminders(bot: Bot):
    """Runs at 8:45 PM WAT to send a private DM reminder to everyone who RSVP'd."""
    now_wat = datetime.now(WAT_TZ)
    today_name = now_wat.strftime("%A")
    event_data = DAILY_SCHEDULE.get(today_name)
    
    if not event_data:
        return
        
    title = event_data["title"]
    if today_name == "Wednesday":
        from datetime import timedelta
        if (now_wat + timedelta(days=7)).month != now_wat.month:
            title = "Wisdom Wednesday (Monthly Book Review!)"
        
    try:
        supabase = SupabaseGateway(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
        event_service = EventService(supabase)
        
        # 1. Find today's event from the database (filtering by today's date)
        today_start = now_wat.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        event = await event_service.find_event_by_title_and_date(title, today_start)
        
        if not event:
            return
            
        event_id = event["id"]
        
        # 2. Get all users who RSVP'd coming
        participants = await event_service.get_event_participants_metadata(event_id, "coming")
        
        if not participants:
            return
            
        user_service = UserService(supabase)
        
        # 3. Send them a DM!
        for p in participants:
            telegram_id = p["metadata"].get("telegram_id")
            first_name = p["metadata"].get("first_name", "YouTopian")
            if telegram_id:
                # 3a. Check if the user has reminders turned OFF
                user = await user_service.get_by_telegram_id(telegram_id)
                if user:
                    user_state = await user_service.get_user_state(user["id"], "eddy")
                    if user_state.get("reminders_enabled", True) is False:
                        continue
                        
                try:
                    await bot.send_message(
                        chat_id=telegram_id,
                        text=f"⏰ <b>Wake up, {first_name}!</b>\n\n<b>{title}</b> is starting in exactly 15 minutes in the Main Group! Grab your notes and get ready. 🚀",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to send DM to {telegram_id}: {e}")
                    
    except Exception as e:
        logger.error(f"Error in send_event_reminders: {e}")

async def trigger_live_event(bot: Bot, group_chat_id: int):
    """Runs every day at 9:00 PM WAT."""
    now_wat = datetime.now(WAT_TZ)
    today_name = now_wat.strftime("%A")
    event_data = DAILY_SCHEDULE.get(today_name)
    
    if not event_data:
        return
        
    title = event_data["title"]
    if today_name == "Wednesday":
        from datetime import timedelta
        if (now_wat + timedelta(days=7)).month != now_wat.month:
            title = "Wisdom Wednesday (Monthly Book Review!)"
        
    message = f"🚨 <b>{title} IS STARTING NOW!</b> 🚨\n\nHead to the main chat and let's go!"
        
    try:
        await bot.send_message(group_chat_id, message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to send 9PM trigger: {e}")

def setup_eddy_scheduler(bot: Bot):
    """Initializes the APScheduler for Eddy's cron jobs."""
    scheduler = AsyncIOScheduler(timezone="Africa/Lagos")
    main_group_id = int(os.getenv("MAIN_GROUP_ID", "0"))
    
    # 1. Announce the event at 5:00 PM
    scheduler.add_job(
        post_daily_announcement,
        CronTrigger(hour=17, minute=0, timezone="Africa/Lagos"),
        args=[bot, main_group_id]
    )
    
    # 2. Send Group Reminder at 8:00 PM
    scheduler.add_job(
        send_group_reminder,
        CronTrigger(hour=20, minute=0, timezone="Africa/Lagos"),
        args=[bot, main_group_id]
    )
    
    # 3. Send private DM Reminders at 8:45 PM
    scheduler.add_job(
        send_event_reminders,
        CronTrigger(hour=20, minute=45, timezone="Africa/Lagos"),
        args=[bot]
    )
    
    # 4. Trigger live event at 9:00 PM
    scheduler.add_job(
        trigger_live_event,
        CronTrigger(hour=21, minute=0, timezone="Africa/Lagos"),
        args=[bot, main_group_id]
    )
    
    scheduler.start()
    logger.info("Eddy's timezone-aware scheduler has started (Africa/Lagos)")
