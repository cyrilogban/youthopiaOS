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
    # Register the group chat for tracking.  Returns None for DMs.
    chat = await register_group_chat(message, services, "theo")

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
        settings_row = await services.supabase.find_one_multi(
            "chat_bot_settings",
            {"bot_name": "theo", "chat_id": chat["id"]},
        )
        if settings_row and "settings" in settings_row:
            translation = settings_row["settings"].get("translation", "kjv")
    else:
        user = await services.identity.resolve_telegram_user(message.from_user)
        user_state = await services.supabase.find_one_multi(
            "bot_user_state",
            {"bot_name": "theo", "user_id": user["id"]}
        )
        if user_state and "state" in user_state:
            translation = user_state["state"].get("translation", "kjv")

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
    await message.reply(reply_text, parse_mode="HTML")
