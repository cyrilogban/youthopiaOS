"""Bible reference auto-detection handler.

Listens for text messages containing Bible references (e.g. ``John 3:16``,
``1 cor 13:4-7``), fetches the verse text from bible-api.com using the
group's preferred translation, and replies to the original message.
"""

from __future__ import annotations

import logging

from aiogram.types import Message

from bots.theo.utils.bible_ref_parser import find_scripture_references
from bots.theo.services.devotional_service import VOTDService
from core.telegram_runtime import register_group_chat
from shared.services.container import ServiceContainer

logger = logging.getLogger(__name__)


async def handle_bible_detection(message: Message, services: ServiceContainer) -> None:
    """Detect Bible references in a message and reply with the verse text.

    Also handles group-chat registration (the same job the fallback
    handler does for non-text messages).
    """
    chat = None
    try:
        chat = await register_group_chat(message, services, "theo")
    except Exception as e:
        logging.warning("Error registering group chat in handle_bible_detection: %s", e)

    if not message.text:
        return

    # Detect scripture references in the message text
    refs = find_scripture_references(message.text)
    if not refs:
        return

    # ------------------------------------------------------------------
    # Resolve translation
    #   Groups  → stored setting from /translation command
    #   DMs     → bot_user_state
    # ------------------------------------------------------------------
    translation = "kjv"

    if chat:
        try:
            settings = await services.chats.get_bot_settings("theo", chat["id"])
            translation = settings.get("translation", "kjv")
        except Exception as e:
            logger.warning("Error fetching group bot settings for theo: %s", e)
            translation = "kjv"
    else:
        try:
            user = await services.identity.resolve_telegram_user(message.from_user)
            user_state = await services.users.get_user_state(user["id"], "theo")
            translation = user_state.get("translation", "kjv")
        except Exception:
            translation = "kjv"

    # ------------------------------------------------------------------
    # Fetch verse texts from bible-api.com
    # ------------------------------------------------------------------
    votd_service = VOTDService(services.supabase)
    parts: list[str] = []

    for ref in refs:
        text = await votd_service.fetch_bible_text(ref.reference, translation)
        if text:
            header = f"<b>{ref.reference} ({translation.upper()})</b>"
            
            # Use expandable blockquotes for verse ranges, standard for single verses
            if ref.is_range:
                blockquote = f"<blockquote expandable>{text}</blockquote>"
            else:
                blockquote = f"<blockquote>{text}</blockquote>"
                
            parts.append(f"{header}\n{blockquote}")
        else:
            parts.append(f"{ref.reference} is not a valid Bible reference.")

    if not parts:
        return

    # ------------------------------------------------------------------
    # Reply — tags the original message so the verse appears under it
    # ------------------------------------------------------------------
    reply_text = "\n\n".join(parts)
    
    markup = None
    if len(refs) == 1:
        from bots.theo.utils.keyboards import build_verse_actions_keyboard
        is_group = message.chat.type != "private"
        bot_me = await message.bot.get_me()
        markup = build_verse_actions_keyboard(
            category="general", 
            reference=refs[0].reference, 
            is_group=is_group,
            bot_username=bot_me.username,
            trans=translation
        )
        
    await message.reply(reply_text, parse_mode="HTML", reply_markup=markup)
