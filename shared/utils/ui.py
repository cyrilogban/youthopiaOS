from __future__ import annotations

from typing import Any, List, Optional
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
)

# -----------------------------------------------------------------------------
# GLOBAL COMMUNITY LINKS (Used across all bots)
# -----------------------------------------------------------------------------

FACEBOOK_LINK = "https://www.facebook.com/share/g/18wG8aWB6t/"
TELEGRAM_GROUP_LINK = "https://t.me/youthopiabiblecommunity"
WHATSAPP_LINK = "https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn"


def get_community_links_keyboard() -> InlineKeyboardMarkup:
    """Returns the standardized community links inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Join Facebook", url=FACEBOOK_LINK),
                InlineKeyboardButton(text="Join Telegram", url=TELEGRAM_GROUP_LINK),
            ],
            [
                InlineKeyboardButton(text="Join WhatsApp", url=WHATSAPP_LINK),
                InlineKeyboardButton(text="Join Threads", callback_data="global_ignore"),
            ],
        ]
    )


# -----------------------------------------------------------------------------
# GLOBAL BOT FAMILY DIRECTORY (Used across all help cards)
# -----------------------------------------------------------------------------

BOT_FAMILY_DIRECTORY_TEXT = (
    "<b>Meet the YouThopia Bot Family</b>\n"
    "<blockquote>"
    "📖 <b>Theo</b> | Daily Word - @iamtheobot\n"
    "🎮 <b>Lusy</b> | Games & XP - @iamlusybot\n"
    "🛡️ <b>Pete</b> | Safety Bot - @iampetebot\n"
    "📅 <b>Ed</b> | Events Bot - @iamedyybot\n"
    "🎵 <b>Susy</b> | Welcome Bot - @iamsusiebot"
    "</blockquote>"
)


# -----------------------------------------------------------------------------
# GLOBAL REPLY KEYBOARD ROW (Row 2 for persistent keyboards)
# -----------------------------------------------------------------------------

GLOBAL_REPLY_BUTTONS: List[KeyboardButton] = [
    KeyboardButton(text="👤 My Profile"),
    KeyboardButton(text="ℹ️ Help"),
    KeyboardButton(text="🌐 Community Links"),
]


# -----------------------------------------------------------------------------
# SHARED PROFILE CARD BUILDER
# -----------------------------------------------------------------------------

def render_shared_profile_card(
    user_data: dict[str, Any],
    telegram_first_name: str,
    bot_specific_stats: Optional[List[str]] = None
) -> str:
    """
    Renders the unified YouTopian profile card format across all bots.
    
    Structure:
    👤 [Display Name]
    ━━━━━━━━━━━━━━━━
    🏅 Level: [Level]
    ⭐ XP: [XP Points]
    🛡️ Trust Score: [Score]/100
    ━━━━━━━━━━━━━━━━
    [Bot-Specific Stats Below]
    """
    display_name = user_data.get("display_name") or telegram_first_name or "YouTopian"
    level = user_data.get("level", 1)
    xp = user_data.get("total_xp", 0)
    trust = user_data.get("trust_score", 100)

    card_lines = [
        f"👤 <b>{display_name}</b>",
        "━━━━━━━━━━━━━━━━",
        f"🏅 Level: <b>{level}</b>",
        f"⭐ XP: <b>{xp}</b>",
        f"🛡️ Trust Score: <b>{trust}/100</b>",
        "━━━━━━━━━━━━━━━━"
    ]

    if bot_specific_stats:
        card_lines.extend(bot_specific_stats)

    return "\n".join(card_lines)
