from __future__ import annotations

import logging
from typing import Any, List, Optional
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
)
from shared.services.container import ServiceContainer

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# GLOBAL COMMUNITY LINKS (Used across all bots)
# -----------------------------------------------------------------------------

FACEBOOK_LINK = "https://www.facebook.com/share/g/18wG8aWB6t/"
TELEGRAM_GROUP_LINK = "https://t.me/youthopiabiblecommunity"
WHATSAPP_LINK = "https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn"


class GroupNoticeCoordinator:
    """In-memory first-responder lock to prevent duplicate group feedback across bots."""
    _claims: dict[str, float] = {}

    @classmethod
    def claim(cls, key: str, ttl_seconds: float = 15.0) -> bool:
        import time
        now = time.time()
        # Clean expired keys
        cls._claims = {k: exp for k, exp in cls._claims.items() if exp > now}
        if key in cls._claims:
            return False
        cls._claims[key] = now + ttl_seconds
        return True


def get_5bot_quick_access_keyboard() -> InlineKeyboardMarkup:
    """Standardized 5-bot quick access inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Theo", url="https://t.me/iamtheobot?start=profile"),
                InlineKeyboardButton(text="🎯 Lusy", url="https://t.me/iamlusybot?start=profile"),
                InlineKeyboardButton(text="🛡️ Pete", url="https://t.me/iampetebot?start=profile"),
            ],
            [
                InlineKeyboardButton(text="📅 Eddy", url="https://t.me/iamedyybot?start=profile"),
                InlineKeyboardButton(text="🌸 Susy", url="https://t.me/iamsusiebot?start=profile"),
            ],
        ]
    )


async def handle_group_profile_acknowledgment(message: Message, bot: Any) -> None:
    """
    Ensures exactly ONE bot in any group posts a 10-second self-destruct acknowledgment notice
    when /profile is typed, regardless of which combination of bots are present in the chat.
    """
    key = f"profile:{message.chat.id}:{message.message_id}"
    if not GroupNoticeCoordinator.claim(key, ttl_seconds=15.0):
        return

    import asyncio
    try:
        await message.delete()
    except Exception:
        pass

    user_first = message.from_user.first_name if message.from_user else "Friend"
    markup = get_5bot_quick_access_keyboard()
    try:
        sent_msg = await message.answer(
            f"<blockquote>🌸 👤 <b>{user_first}</b>, your community profiles from our 5 ecosystem bots have been sent to your private DMs!\n\n"
            f"<i>Tap below if you haven't unlocked a specific bot yet:</i></blockquote>",
            parse_mode="HTML",
            reply_markup=markup
        )
        async def _cleanup():
            await asyncio.sleep(10)
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
            except Exception:
                pass
        asyncio.create_task(_cleanup())
    except Exception as e:
        logger.warning(f"Failed to send group profile notice: {e}")


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
    KeyboardButton(text="🌐 Community"),
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


# -----------------------------------------------------------------------------
# GLOBAL COMMUNITY EXPLORATION TOUR (Synchronized across all 5 bots)
# -----------------------------------------------------------------------------

async def send_community_exploration_page(message: Message, page: int, edit: bool = False) -> None:
    """Renders pages of the unified YouThopia Community Exploration Tour."""
    if page == 1:
        text = (
            "<b>Welcome to YOUTHOPIA! 🤍 (1/3)</b>\n"
            "<blockquote>We are a cross-platform Gen Z Christian community. This is a space where faith meets real life. "
            "We grow together, share God's Word, and support one another on the journey of becoming who God created us to be.</blockquote>\n\n"
            "<i>Click Next to read our community guidelines.</i>"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Next ➡️", callback_data="onboarding_2")]
        ])
    elif page == 2:
        text = (
            "<b>The Core Rules 📜 (2/3)</b>\n"
            "<blockquote><b>1. Love & Respect:</b> Treat everyone with Christ-like love.\n"
            "<b>2. No Spam:</b> Keep the chat clean and focused on growth.\n"
            "<b>3. Guard the Vibe:</b> Keep conversations edifying and uplifting.</blockquote>\n\n"
            "<i>Click Next to meet the YouThopia Bot Family!</i>"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Back", callback_data="onboarding_1"),
                InlineKeyboardButton(text="Next ➡️", callback_data="onboarding_3")
            ]
        ])
    else:  # Page 3
        text = (
            "<b>Meet the Bot Family 🤖 (3/3)</b>\n"
            "<blockquote><b>Theo</b> (@iamtheobot) - Your daily devotional companion.\n"
            "<b>Lusy</b> (@iamlusybot) - Play games and earn YP!\n"
            "<b>Pete</b> (@iampetebot) - The security guard.\n"
            "<b>Ed</b> (@iamedyybot) - Announcements and events.\n"
            "<b>Susy</b> (@iamsusiebot) - Your guide and friend.</blockquote>\n\n"
            "<i>Click Finish to complete your orientation!</i>"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Back", callback_data="onboarding_2"),
                InlineKeyboardButton(text="✅ Finish Exploring", callback_data="onboarding_finish")
            ]
        ])

    if edit:
        await message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=markup)


async def handle_global_onboarding_callback(callback_query: CallbackQuery, services: ServiceContainer) -> None:
    """Handles global onboarding callbacks with synchronized point protection across all 5 bots."""
    action = callback_query.data.split("_")[1]

    if action in ["1", "2", "3"]:
        await send_community_exploration_page(callback_query.message, int(action), edit=True)
        await callback_query.answer()
    elif action == "finish":
        user = await services.identity.resolve_telegram_user(callback_query.from_user)

        # Check if user has already completed orientation globally in Supabase
        already_completed = False
        if user.get("engagement_level") == "onboarded":
            already_completed = True
        else:
            try:
                actions = await services.supabase.find_many("moderation_actions", {"user_id": user["id"], "action_type": "orientation_completed"})
                if actions:
                    already_completed = True
            except Exception:
                pass

        if not already_completed:
            try:
                await services.users.set_engagement_level(user["id"], "onboarded")
            except Exception as e:
                logger.warning(f"Failed to set engagement_level: {e}")

            try:
                await services.moderation.record_action(
                    user_id=user["id"],
                    action_type="orientation_completed",
                    reason="Completed community exploration guide.",
                    trust_delta=50
                )
            except Exception as e:
                logger.warning(f"Failed to record orientation action: {e}")

            finish_text = (
                "<b>Exploration Complete! 🎉</b>\n"
                "<blockquote>You are now officially a YouTopian! I've granted you <b>+50 Trust Points</b> for completing your exploration.</blockquote>\n\n"
                "Connect with us across all platforms below: 💜"
            )
            await callback_query.answer("Exploration Complete! +50 Trust Points!")
        else:
            finish_text = (
                "<b>Exploration Reviewed!</b>\n"
                "<blockquote>It looks like you've already completed your official exploration! No extra points were granted, but it's great to refresh your memory.</blockquote>\n\n"
                "Connect with us across all platforms below: 💜"
            )
            await callback_query.answer("Exploration Reviewed!")

        await callback_query.message.edit_text(
            finish_text, parse_mode="HTML", reply_markup=get_community_links_keyboard()
        )
