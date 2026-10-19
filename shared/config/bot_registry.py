"""Centralized Bot Identity Registry for YouThopiaOS.

Defines the single source of truth for the 5 Telegram bots:
- Theo (@theobiblebot)
- Susie (@susiehelpsbot)
- Edie (@ediecalendarbot)
- Pete (@petemodbot)
- Lusie (@lusiequizbot)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

# One base URL, one deployment. Each bot opens its own React Router route on it.
MINI_APP_BASE_URL = "https://youthopiaos.onrender.com"


@dataclass(frozen=True, slots=True)
class BotIdentity:
    internal_name: str  # e.g., "theo", "susy", "eddy", "pete", "lusy"
    full_name: str      # e.g., "Theodore", "Susan", "Edmund", "Peter", "Lucy"
    short_name: str     # e.g., "Theo", "Susie", "Edie", "Pete", "Lusie"
    username: str       # e.g., "theobiblebot", "susiehelpsbot", "ediecalendarbot", "petemodbot", "lusiequizbot"
    emoji: str          # e.g., "📖", "💬", "📅", "🛡️", "🎯"
    tagline: str        # e.g., "Daily Word", "Welcome Bot", "Events Bot", "Safety Bot", "Games & XP"
    responsibility: str # High-level summary of responsibilities
    route_slug: str     # Mini App route for this bot, e.g., "theo", "susie", "edie", "pete", "lusie"

    @property
    def display_name(self) -> str:
        return f"{self.full_name} ({self.short_name})"

    @property
    def greeting_intro(self) -> str:
        return f"I am {self.full_name}, but you can call me {self.short_name}!"

    @property
    def handle(self) -> str:
        return f"@{self.username}"

    @property
    def link(self) -> str:
        return f"https://t.me/{self.username}"

    @property
    def mini_app_link(self) -> str:
        """Main Mini App direct link, opens in the current chat (group-safe).

        Uses the ``?startapp`` format because that is the main Mini App link set
        via BotFather; the ``/app`` form would require a separate /newapp short
        name "app" for every bot.
        """
        return f"https://t.me/{self.username}?startapp"

    @property
    def mini_app_route_url(self) -> str:
        """Direct Mini App route for this bot, e.g. https://youthopiaos.onrender.com/theo."""
        return f"{MINI_APP_BASE_URL}/{self.route_slug}"

    def get_start_link(self, parameter: str = "") -> str:
        if parameter:
            return f"https://t.me/{self.username}?start={parameter}"
        return self.link

    def get_group_invite_link(self, admin_params: str = "") -> str:
        if admin_params:
            return f"https://t.me/{self.username}?startgroup=admin&admin={admin_params}"
        return f"https://t.me/{self.username}?startgroup=true"


BOT_REGISTRY: Dict[str, BotIdentity] = {
    "theo": BotIdentity(
        internal_name="theo",
        full_name="Theodore",
        short_name="Theo",
        username="theobiblebot",
        emoji="📖",
        tagline="Daily Word",
        responsibility="Scripture, devotionals, saved verses, and theological assistance",
        route_slug="theo",
    ),
    "susy": BotIdentity(
        internal_name="susy",
        full_name="Susan",
        short_name="Susie",
        username="susiehelpsbot",
        emoji="💬",
        tagline="Welcome Bot",
        responsibility="Welcome messages, onboarding, and community hospitality",
        route_slug="susie",
    ),
    "eddy": BotIdentity(
        internal_name="eddy",
        full_name="Edmund",
        short_name="Edie",
        username="ediecalendarbot",
        emoji="📅",
        tagline="Events Bot",
        responsibility="Community calendar, event management, meetings, birthdays, schedules, and reminders",
        route_slug="edie",
    ),
    "pete": BotIdentity(
        internal_name="pete",
        full_name="Peter",
        short_name="Pete",
        username="petemodbot",
        emoji="🛡️",
        tagline="Safety Bot",
        responsibility="Anti-spam, anti-bot detection, moderation, and community protection",
        route_slug="pete",
    ),
    "lusy": BotIdentity(
        internal_name="lusy",
        full_name="Lucy",
        short_name="Lusie",
        username="lusiequizbot",
        emoji="🎯",
        tagline="Games & XP",
        responsibility="Bible quizzes, XP, competitions, and leaderboards",
        route_slug="lusie",
    ),
}

# Base Mini App URL (redirects to /home). Prefer a bot's mini_app_route_url so
# each bot opens its own routed experience.
DEFAULT_MINI_APP_LINK = MINI_APP_BASE_URL


def get_bot_identity(internal_name: str) -> BotIdentity:
    if internal_name not in BOT_REGISTRY:
        raise KeyError(f"Unknown bot internal_name: {internal_name}")
    return BOT_REGISTRY[internal_name]


def meet_description(internal_name: str) -> str:
    """Registry-derived /start menu description, e.g. "Meet Theodore (Theo)"."""
    identity = get_bot_identity(internal_name)
    return f"Meet {identity.full_name} ({identity.short_name})"
