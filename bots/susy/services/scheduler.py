from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from shared.db.supabase import SupabaseGateway
import os

logger = logging.getLogger(__name__)
WAT_TZ = ZoneInfo("Africa/Lagos")

async def celebrate_birthdays(bot: Bot, group_chat_id: int):
    """Runs every day at 8:00 AM WAT to celebrate birthdays."""
    now_wat = datetime.now(WAT_TZ)
    current_month = now_wat.month
    current_day = now_wat.day
    
    try:
        supabase = SupabaseGateway(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
        
        # Fetch all Susy states
        # Since the community is small, we can fetch all and filter in Python to avoid complex JSONB querying issues
        response = supabase._client().table("bot_user_state").select("user_id, state").eq("bot_name", "susy").execute()
        states = response.data or []
        
        for record in states:
            state_data = record.get("state", {})
            b_month = state_data.get("birthday_month")
            b_day = state_data.get("birthday_day")
            
            if b_month == current_month and b_day == current_day:
                user_id = record["user_id"]
                
                # Fetch their telegram account info
                account_resp = supabase._client().table("telegram_accounts").select("telegram_id, first_name, username").eq("user_id", user_id).execute()
                if not account_resp.data:
                    continue
                    
                account = account_resp.data[0]
                first_name = account.get("first_name", "YouTopian")
                username = account.get("username")
                
                mention = f"@{username}" if username else f"<b>{first_name}</b>"
                photo_id = state_data.get("birthday_photo_id")
                
                message_text = (
                    f"🎉🎈 <b>STOP EVERYTHING!</b> 🎈🎉\n\n"
                    f"Today is a very special day! Help me wish an incredibly Happy Birthday to our amazing {mention}! 🎂\n\n"
                    f"We are so blessed to have you in the YouThopia family. Keep shining your light!\n\n"
                    f"<i>Everyone drop your wishes below! 👇🥳</i>"
                )
                
                try:
                    if photo_id:
                        await bot.send_photo(group_chat_id, photo=photo_id, caption=message_text, parse_mode="HTML")
                    else:
                        await bot.send_message(group_chat_id, message_text, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Failed to send birthday message for {user_id}: {e}")
                    
    except Exception as e:
        logger.error(f"Error checking birthdays: {e}")

def setup_susy_scheduler(bot: Bot):
    """Initializes the APScheduler for Susy's cron jobs."""
    scheduler = AsyncIOScheduler(timezone="Africa/Lagos")
    main_group_id = int(os.getenv("MAIN_GROUP_ID", "0"))
    
    # Run at 8:00 AM every day
    scheduler.add_job(
        celebrate_birthdays,
        CronTrigger(hour=8, minute=0),
        args=[bot, main_group_id]
    )
    
    scheduler.start()
