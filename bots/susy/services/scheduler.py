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
                telegram_id = account.get("telegram_id")
                if not telegram_id:
                    continue
                    
                first_name = account.get("first_name", "YouTopian")
                photo_id = state_data.get("birthday_photo_id")
                
                # 1. Send Private DM
                dm_text = (
                    f"🎉 <b>HAPPY BIRTHDAY {first_name}!</b> 🎂\n\n"
                    f"I hope you have an absolutely amazing day filled with joy and blessings! "
                    f"We love having you in the YouThopia family! 🤍"
                )
                try:
                    if photo_id:
                        await bot.send_photo(telegram_id, photo=photo_id, caption=dm_text, parse_mode="HTML")
                    else:
                        await bot.send_message(telegram_id, dm_text, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Failed to send private birthday DM to {telegram_id}: {e}")

                # 2. Check if they are in the Main Group (Ghost Check)
                in_group = False
                try:
                    member = await bot.get_chat_member(group_chat_id, telegram_id)
                    if member.status in ["member", "administrator", "creator", "restricted"]:
                        in_group = True
                except Exception as e:
                    logger.error(f"Could not check group membership for {telegram_id}: {e}")
                    
                # 3. Post to the Group (Only if they are in it)
                if in_group:
                    # Invisible Tagging so they get a push notification even without a username
                    mention = f"<a href='tg://user?id={telegram_id}'>{first_name}</a>"
                    
                    group_text = (
                        f"🎉🎈 <b>STOP EVERYTHING!</b> 🎈🎉\n\n"
                        f"Today is a very special day! Help me wish an incredibly Happy Birthday to our amazing {mention}! 🎂\n\n"
                        f"We are so blessed to have you in the YouThopia family. Keep shining your light!\n\n"
                        f"<i>Everyone drop your wishes below! 👇🥳</i>"
                    )
                    
                    try:
                        if photo_id:
                            await bot.send_photo(group_chat_id, photo=photo_id, caption=group_text, parse_mode="HTML")
                        else:
                            await bot.send_message(group_chat_id, group_text, parse_mode="HTML")
                    except Exception as e:
                        logger.error(f"Failed to send group birthday message for {user_id}: {e}")
                    
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
