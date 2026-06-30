from __future__ import annotations

import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shared.services.event_service import EventService
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

async def post_daily_announcement(bot: Bot, group_chat_id: int):
    """Runs every day at 8:00 PM WAT to announce the 9:00 PM event."""
    today_name = datetime.now().strftime("%A")
    event_data = DAILY_SCHEDULE.get(today_name)
    
    if not event_data:
        return
        
    # Check for Last Wednesday of the Month Book Review
    if today_name == "Wednesday":
        today = datetime.now()
        # Logic: If adding 7 days pushes us into the next month, this is the last Wednesday
        from datetime import timedelta
        if (today + timedelta(days=7)).month != today.month:
            event_data["title"] = "Wisdom Wednesday (Monthly Book Review!)"
            event_data["description"] = "It's the last Wednesday of the month! Join us for our deep-dive Monthly Book review."

    # Initialize Supabase and EventService
    supabase = SupabaseGateway(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
    event_service = EventService(supabase)
    
    # 1. Create the event in the database
    event_payload = {
        "title": event_data["title"],
        "description": event_data["description"],
        "starts_at": datetime.now().replace(hour=21, minute=0, second=0, microsecond=0).isoformat(),
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
        f"<b>Tonight's Event:</b> {event_data['title']}\n"
        f"<blockquote>{event_data['description']}</blockquote>\n\n"
        "We are starting in exactly 1 hour (9:00 PM WAT). Click below to RSVP!"
    )
    
    # 3. Attach the specific event_id to the callback data
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Coming", callback_data=f"rsvp_coming:{event_id}"),
            InlineKeyboardButton(text="❓ Maybe", callback_data=f"rsvp_maybe:{event_id}"),
            InlineKeyboardButton(text="❌ Can't Attend", callback_data=f"rsvp_no:{event_id}")
        ]
    ])
    
    try:
        await bot.send_message(group_chat_id, announcement, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logger.error(f"Failed to send 8PM announcement: {e}")


async def send_event_reminders(bot: Bot):
    """Runs at 8:45 PM WAT to send a private DM reminder to everyone who RSVP'd."""
    today_name = datetime.now().strftime("%A")
    event_data = DAILY_SCHEDULE.get(today_name)
    
    if not event_data:
        return
        
    try:
        supabase = SupabaseGateway(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
        
        # 1. Find today's event from the database (filtering by today's date)
        # For simplicity in this prototype, we'll find the most recent event created today with this title.
        today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        events_resp = supabase.client.table("events").select("id").eq("title", event_data["title"]).gte("created_at", today_start).execute()
        
        if not events_resp.data:
            return
            
        event_id = events_resp.data[0]["id"]
        
        # 2. Get all users who RSVP'd coming
        participants_resp = supabase.client.table("event_participants").select("metadata").eq("event_id", event_id).eq("status", "coming").execute()
        
        if not participants_resp.data:
            return
            
        # 3. Send them a DM!
        for p in participants_resp.data:
            telegram_id = p["metadata"].get("telegram_id")
            first_name = p["metadata"].get("first_name", "YouTopian")
            if telegram_id:
                try:
                    await bot.send_message(
                        chat_id=telegram_id,
                        text=f"⏰ <b>Wake up, {first_name}!</b>\n\n<b>{event_data['title']}</b> is starting in exactly 15 minutes in the Main Group! Grab your notes and get ready. 🚀",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to send DM to {telegram_id}: {e}")
                    
    except Exception as e:
        logger.error(f"Error in send_event_reminders: {e}")

async def trigger_live_event(bot: Bot, group_chat_id: int):
    """Runs every day at 9:00 PM WAT."""
    today_name = datetime.now().strftime("%A")
    event_data = DAILY_SCHEDULE.get(today_name)
    
    if not event_data:
        return
        
    if today_name == "Friday":
        # LUSY SYNC: Tell Lusy to take over!
        message = (
            f"🚨 <b>{event_data['title']} IS LIVE!</b> 🚨\n\n"
            "The weekend is here! Let's get to it. Over to you, @iamlusybot! 🎮"
        )
    else:
        message = f"🚨 <b>{event_data['title']} IS STARTING NOW!</b> 🚨\n\nHead to the main chat and let's go!"
        
    try:
        await bot.send_message(group_chat_id, message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to send 9PM trigger: {e}")

def setup_eddy_scheduler(bot: Bot):
    """Initializes the APScheduler for Eddy's cron jobs."""
    scheduler = AsyncIOScheduler(timezone="Africa/Lagos")
    main_group_id = int(os.getenv("MAIN_GROUP_ID", "0"))
    
    # 1. Announce the event at 8:00 PM
    scheduler.add_job(
        post_daily_announcement,
        CronTrigger(hour=20, minute=0),
        args=[bot, main_group_id]
    )
    
    # 2. Send private DM Reminders at 8:45 PM
    scheduler.add_job(
        send_event_reminders,
        CronTrigger(hour=20, minute=45),
        args=[bot]
    )
    
    # 3. Trigger the actual event at 9:00 PM
    scheduler.add_job(
        trigger_live_event,
        CronTrigger(hour=21, minute=0),
        args=[bot, main_group_id]
    )
    
    scheduler.start()
    logger.info("Eddy's timezone-aware scheduler has started (Africa/Lagos)")
