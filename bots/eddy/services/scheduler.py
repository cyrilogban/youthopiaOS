from __future__ import annotations

import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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

    announcement = (
        f"<b>Happy {today_name}, YouTopians!</b> 🚀\n\n"
        f"<b>Tonight's Event:</b> {event_data['title']}\n"
        f"<blockquote>{event_data['description']}</blockquote>\n\n"
        "We are starting in exactly 1 hour (9:00 PM WAT). Click below to RSVP!"
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Coming", callback_data=f"rsvp_yes"),
            InlineKeyboardButton(text="❓ Maybe", callback_data=f"rsvp_maybe"),
            InlineKeyboardButton(text="❌ Can't Attend", callback_data=f"rsvp_no")
        ]
    ])
    
    try:
        await bot.send_message(group_chat_id, announcement, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logger.error(f"Failed to send 8PM announcement: {e}")


async def trigger_event_start(bot: Bot, group_chat_id: int):
    """Runs every day at 9:00 PM WAT to start the event."""
    today_name = datetime.now().strftime("%A")
    
    start_message = (
        f"🚨 <b>{today_name} Event Starting NOW!</b> 🚨\n\n"
        "Get in here! We are officially starting."
    )
    
    try:
        await bot.send_message(group_chat_id, start_message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to send 9PM start trigger: {e}")


import os

def setup_eddy_scheduler(bot: Bot):
    # APScheduler needs timezone "Africa/Lagos" for West Africa Time (WAT)
    scheduler = AsyncIOScheduler(timezone="Africa/Lagos")
    
    # Get the Main Group ID from .env
    main_group_id = int(os.getenv("MAIN_GROUP_ID", "0"))
    
    # Run at 20:00 (8:00 PM) WAT
    scheduler.add_job(
        post_daily_announcement, 
        trigger="cron", 
        hour=20, 
        minute=0, 
        args=[bot, main_group_id]
    )
    
    # Run at 21:00 (9:00 PM) WAT
    scheduler.add_job(
        trigger_event_start, 
        trigger="cron", 
        hour=21, 
        minute=0, 
        args=[bot, main_group_id]
    )
    
    scheduler.start()
    return scheduler
