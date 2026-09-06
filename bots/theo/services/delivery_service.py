import asyncio
import logging
from dataclasses import dataclass
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from shared.services.container import ServiceContainer
from bots.theo.services.devotional_service import VOTDService
from bots.theo.utils.keyboards import build_verse_actions_keyboard

logger = logging.getLogger(__name__)

@dataclass
class DeliveryService:
    """Service responsible for broadcasting the Verse of the Day to all subscribers."""
    bot: Bot
    services: ServiceContainer

    async def broadcast_votd(self) -> dict:
        """
        Broadcasts today's VOTD to all subscribed chats and users.
        Returns a summary dictionary.
        """
        votd_service = VOTDService(self.services.supabase)
        todays_votd = await votd_service.get_todays_reference()
        
        if not todays_votd:
            logger.warning("DeliveryService: No VOTD scheduled for today.")
            return {"status": "error", "message": "No VOTD scheduled for today."}
        reference = todays_votd["reference"]
        logger.info("Broadcasting VOTD: %s", reference)
        
        # Resolve bot username once to avoid multiple API calls in loops
        bot_me = await self.bot.get_me()
        bot_username = bot_me.username
        
        # We will cache the fetched text by translation to avoid redundant API calls
        fetched_texts: dict[str, str] = {}
        
        # Fetch all active subscriptions
        chat_subs = await self.services.chats.get_active_subscriptions("theo", "daily_devotional")
        user_subs = await self.services.users.get_active_subscriptions("theo", "daily_devotional")
        
        success_count = 0
        failure_count = 0
        
        # 1. Process Group Chat Subscriptions
        for sub in chat_subs:
            chat_id = sub["chat_id"]
            try:
                # Resolve the actual Telegram Chat ID
                chat_record = await self.services.chats.get_chat_by_id(chat_id)
                telegram_chat_id = chat_record["telegram_chat_id"]
                
                # Resolve the group's preferred translation (default to kjv)
                chat_settings = await self.services.chats.get_bot_settings("theo", chat_id)
                translation = chat_settings.get("translation", "kjv")
                
                # Fetch text if we haven't already fetched it for this translation
                if translation not in fetched_texts:
                    text = await votd_service.fetch_bible_text(reference, translation)
                    if text:
                        fetched_texts[translation] = text
                    else:
                        logger.error("Failed to fetch %s in %s", reference, translation)
                        failure_count += 1
                        continue
                        
                text = fetched_texts[translation]
                header = f"<b>Verse of the Day: {reference} ({translation.upper()})</b>"
                blockquote = f"<blockquote expandable>{text}</blockquote>" if len(text) > 150 else f"<blockquote>{text}</blockquote>"
                message = f"{header}\n{blockquote}"
                
                markup = build_verse_actions_keyboard(category="daily", reference=reference, is_group=True, bot_username=bot_username, trans=translation)
                
                metadata = sub.get("metadata") or {}
                message_thread_id = metadata.get("message_thread_id")

                await self.bot.send_message(
                    chat_id=telegram_chat_id, 
                    text=message, 
                    parse_mode="HTML",
                    reply_markup=markup,
                    message_thread_id=message_thread_id,
                )
                success_count += 1
            except Exception as e:
                logger.error("Failed to send VOTD to chat %s: %s", chat_id, e)
                failure_count += 1
                
        # 2. Process Direct Message (User) Subscriptions
        for sub in user_subs:
            user_id = sub["user_id"]
            try:
                # Resolve the actual Telegram User ID
                telegram_account = await self.services.users.get_telegram_account_by_user_id(user_id)
                if not telegram_account:
                    continue
                telegram_user_id = telegram_account["telegram_id"]
                
                # Default translation for users (could be expanded to user settings later)
                translation = "kjv"
                
                if translation not in fetched_texts:
                    text = await votd_service.fetch_bible_text(reference, translation)
                    if text:
                        fetched_texts[translation] = text
                    else:
                        failure_count += 1
                        continue
                        
                text = fetched_texts[translation]
                header = f"<b>Verse of the Day: {reference} ({translation.upper()})</b>"
                blockquote = f"<blockquote expandable>{text}</blockquote>" if len(text) > 150 else f"<blockquote>{text}</blockquote>"
                message = f"{header}\n{blockquote}"
                
                markup = build_verse_actions_keyboard(category="daily", reference=reference, is_group=False, bot_username=bot_username, trans=translation)
                
                await self.bot.send_message(
                    chat_id=telegram_user_id, 
                    text=message, 
                    parse_mode="HTML",
                    reply_markup=markup
                )
                success_count += 1
            except Exception as e:
                logger.error("Failed to send VOTD to user %s: %s", user_id, e)
                failure_count += 1
                
        logger.info("VOTD Broadcast complete. Success: %d, Failures: %d", success_count, failure_count)
        return {
            "status": "success", 
            "reference": reference, 
            "success_count": success_count, 
            "failure_count": failure_count
        }
