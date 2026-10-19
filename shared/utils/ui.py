from __future__ import annotations

import logging
from typing import Any, List, Optional
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    WebAppInfo,
)
from shared.services.container import ServiceContainer
from shared.config.bot_registry import BOT_REGISTRY, MINI_APP_BASE_URL, get_bot_identity
from shared.content import tour as tour_content

logger = logging.getLogger(__name__)

MINI_APP_URL = MINI_APP_BASE_URL


def get_open_app_inline_button(bot_name: Optional[str] = None) -> InlineKeyboardButton:
    """Inline Mini App launcher. Pass a bot name to open that bot's route."""
    url = get_bot_identity(bot_name).mini_app_route_url if bot_name else MINI_APP_URL
    return InlineKeyboardButton(text="Open App", web_app=WebAppInfo(url=url))


def get_open_app_reply_button(bot_name: Optional[str] = None) -> KeyboardButton:
    """Reply-keyboard Mini App launcher. Pass a bot name to open that bot's route."""
    url = get_bot_identity(bot_name).mini_app_route_url if bot_name else MINI_APP_URL
    return KeyboardButton(text="Open App", web_app=WebAppInfo(url=url))

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
                InlineKeyboardButton(text="📖 Theo", url="https://t.me/theobiblebot?start=profile"),
                InlineKeyboardButton(text="🎯 Lusie", url="https://t.me/lusiequizbot?start=profile"),
                InlineKeyboardButton(text="🛡️ Pete", url="https://t.me/petemodbot?start=profile"),
            ],
            [
                InlineKeyboardButton(text="📅 Edie", url="https://t.me/ediecalendarbot?start=profile"),
                InlineKeyboardButton(text="💬 Susie", url="https://t.me/susiehelpsbot?start=profile"),
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
            f"<blockquote>👤 <b>{user_first}</b>, your community profiles from our 5 ecosystem bots have been sent to your private DMs!\n\n"
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


COMMUNITY_LINKS_CARD_TEXT = (
    "<b>🌐 YOUTHOPIA BIBLE COMMUNITY LINKS</b>\n"
    "<blockquote>Connect with us across all platforms to stay updated, fellowship, "
    "and grow together! 🤍</blockquote>"
)


async def send_community_links_card(message: Message) -> None:
    """Sends the standard community links card (the '🌐 Community' reply button)."""
    await message.answer(
        COMMUNITY_LINKS_CARD_TEXT,
        parse_mode="HTML",
        reply_markup=get_community_links_keyboard(),
    )


# -----------------------------------------------------------------------------
# GLOBAL BOT FAMILY DIRECTORY (Used across all help cards)
# -----------------------------------------------------------------------------

BOT_FAMILY_DIRECTORY_TEXT = (
    "<b>Meet the YouThopia Bot Family</b>\n"
    "<blockquote>"
    "📖 <b>Theodore (Theo)</b> | Daily Word - @theobiblebot\n"
    "🎮 <b>Lucy (Lusie)</b> | Games & XP - @lusiequizbot\n"
    "🛡️ <b>Peter (Pete)</b> | Safety Bot - @petemodbot\n"
    "📅 <b>Edmund (Edie)</b> | Events Bot - @ediecalendarbot\n"
    "💬 <b>Susan (Susie)</b> | Welcome Bot - @susiehelpsbot"
    "</blockquote>"
)


# -----------------------------------------------------------------------------
# GLOBAL REPLY KEYBOARD ROW (Row 2 for persistent keyboards)
# -----------------------------------------------------------------------------

GLOBAL_REPLY_BUTTONS: List[KeyboardButton] = [
    KeyboardButton(text="My Profile"),
    KeyboardButton(text="Take Tour"),
    KeyboardButton(text="Help"),
    KeyboardButton(text="Community"),
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
    🏅 Rank: [Emoji] [Rank Title] (Lvl [Level])
    ━━━━━━━━━━━━━━━━
    ⭐ XP: [XP Points] YP
    🛡️ Trust Score: [Score]/100
    ━━━━━━━━━━━━━━━━
    [Bot-Specific Stats Below]
    """
    from shared.services.rank_service import RankService
    from shared.services.xp_service import calculate_level

    display_name = user_data.get("display_name") or telegram_first_name or "YouTopian"
    xp = user_data.get("total_xp", 0)
    level = user_data.get("level") or calculate_level(xp)
    if level == 1 and xp > 0:
        level = calculate_level(xp)
    trust = user_data.get("trust_score", 100)
    manual_rank = user_data.get("manual_rank_id")
    rank = RankService.resolve_rank(xp, manual_rank)

    card_lines = [
        f"👤 <b>{display_name}</b>",
        f"🏅 Rank: <b>{rank.emoji} {rank.title}</b> (Lvl {level})",
        "━━━━━━━━━━━━━━━━",
        f"⭐ XP: <b>{xp} YP</b>",
        f"🛡️ Trust Score: <b>{trust}/100</b>",
        "━━━━━━━━━━━━━━━━"
    ]

    if bot_specific_stats:
        card_lines.extend(bot_specific_stats)

    return "\n".join(card_lines)


# -----------------------------------------------------------------------------
# GLOBAL COMMUNITY EXPLORATION TOUR (Synchronized across all 5 bots)
# -----------------------------------------------------------------------------

def _bullets(items: tuple[str, ...]) -> str:
    return "\n".join(f"• {item}" for item in items)


def _bot_family_roster() -> str:
    lines = [
        f"<b>{identity.display_name}</b> — {identity.tagline} <a href=\"{identity.link}\">{identity.handle}</a>\n"
        f"<i>{identity.responsibility}</i>\n"
        for identity in BOT_REGISTRY.values()
    ]
    return "\n".join(lines)


def build_tour_keyboard(page: int) -> InlineKeyboardMarkup:
    """Navigation keyboard for the unified YouThopia Tour (5 pages)."""
    total = tour_content.TOUR_TOTAL_PAGES
    if page <= 1:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Next", callback_data="onboarding_2")]
        ])
    if page >= total:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Back", callback_data=f"onboarding_{total - 1}"),
            InlineKeyboardButton(text="Finish Tour", callback_data="onboarding_finish"),
        ]])
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Back", callback_data=f"onboarding_{page - 1}"),
        InlineKeyboardButton(text="Next", callback_data=f"onboarding_{page + 1}"),
    ]])


async def send_community_exploration_page(message: Message, page: int, edit: bool = False) -> None:
    """Renders pages of the unified YouThopia Community Tour (identical on all 5 bots + Mini App)."""
    total = tour_content.TOUR_TOTAL_PAGES
    slogan = f"<b>The YouThopia Tour ({page}/{total})</b>"

    if page == 1:
        text = (
            f"{slogan}\n"
            "<b>About YouThopia</b>\n"
            f"<blockquote>{tour_content.ABOUT_TEXT}</blockquote>\n\n"
            "<b>Our Vision</b>\n"
            f"<blockquote><i>{tour_content.VISION_TEXT}</i></blockquote>"
        )
    elif page == 2:
        text = (
            f"{slogan}\n"
            "<b>Our Mission</b>\n"
            f"<blockquote>{_bullets(tour_content.MISSION_BULLETS)}</blockquote>"
        )
    elif page == 3:
        text = (
            f"{slogan}\n"
            "<b>Aims &amp; Objectives</b>\n"
            f"<blockquote>{_bullets(tour_content.AIMS_BULLETS)}</blockquote>"
        )
    elif page == 4:
        text = (
            f"{slogan}\n"
            "<b>Five Pillars, One Family</b>\n"
            f"<blockquote>{_bot_family_roster()}</blockquote>\n\n"
            "<i>Each pillar has its own duty — together we grow, connect, and shine as one family in CHRIST.</i>"
        )
    else:  # Page 5
        text = (
            f"{slogan}\n"
            "<b>Your Journey</b>\n"
            "<blockquote>Every YouTopian grows through 9 ranks of grace — from <b>The Seeker</b> to "
            "<b>YouThopia’s Ambassador</b>. Earn <b>YP</b> by engaging in the community: quizzes, "
            "devotionals, events, fellowship, and your Trust Score reflects your reliability and integrity.</blockquote>\n\n"
            "<i>Tap Finish to be marked as oriented, receive a welcome boost, and connect with us below!</i>"
        )

    markup = build_tour_keyboard(page)

    if edit:
        await message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=markup)


async def handle_global_onboarding_callback(callback_query: CallbackQuery, services: ServiceContainer) -> None:
    """Handles global onboarding callbacks with synchronized point protection across all 5 bots."""
    action = callback_query.data.split("_")[1]

    if action == "start":
        # Legacy welcome-card buttons ("Take Community Tour") open page 1.
        await send_community_exploration_page(callback_query.message, 1, edit=True)
        await callback_query.answer()
        return
    if action.isdigit() and 1 <= int(action) <= tour_content.TOUR_TOTAL_PAGES:
        await send_community_exploration_page(callback_query.message, int(action), edit=True)
        await callback_query.answer()
        return
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

            try:
                await services.xp.award_xp(
                    user_id=user["id"],
                    amount=50,
                    bot_name="susy",
                    source="onboarding_tour",
                    idempotency_key=f"onboarding_xp_{user['id']}"
                )
            except Exception as e:
                logger.warning(f"Failed to award onboarding XP: {e}")

            finish_text = (
                "<b>Exploration Complete!</b>\n"
                "<blockquote>Congratulations! You have advanced to <b>YouTopian Gathered One</b>!\n"
                "You have been awarded <b>+50 YP</b> & <b>+50 Trust Points</b> for completing your orientation.</blockquote>\n\n"
                "Connect with us across all platforms below:"
            )
            await callback_query.answer("Advanced to YouTopian Gathered One! (+50 YP)")
        else:
            finish_text = (
                "<b>Exploration Reviewed!</b>\n"
                "<blockquote>It looks like you've already completed your official exploration! No extra points were granted, but it's great to refresh your memory.</blockquote>\n\n"
                "Connect with us across all platforms below:"
            )
            await callback_query.answer("Exploration Reviewed!")

        await callback_query.message.edit_text(
            finish_text, parse_mode="HTML", reply_markup=get_community_links_keyboard()
        )
