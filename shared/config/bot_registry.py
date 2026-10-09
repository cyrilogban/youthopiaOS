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


@dataclass(frozen=True, slots=True)
class BotIdentity:
    internal_name: str  # e.g., "theo", "susy", "eddy", "pete", "lusy"
    full_name: str      # e.g., "Theodore", "Susan", "Edmund", "Peter", "Lucy"
    short_name: str     # e.g., "Theo", "Susie", "Edie", "Pete", "Lusie"
    username: str       # e.g., "theobiblebot", "susiehelpsbot", "ediecalendarbot", "petemodbot", "lusiequizbot"
    emoji: str          # e.g., "📖", "💬", "📅", "🛡️", "🎯"
    tagline: str        # e.g., "Daily Word", "Welcome Bot", "Events Bot", "Safety Bot", "Games & XP"
    responsibility: str # High-level summary of responsibilities

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
        return f"https://t.me/{self.username}/app"

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
    ),
    "susy": BotIdentity(
        internal_name="susy",
        full_name="Susan",
        short_name="Susie",
        username="susiehelpsbot",
        emoji="💬",
        tagline="Welcome Bot",
        responsibility="Welcome messages, onboarding, and community hospitality",
    ),
    "eddy": BotIdentity(
        internal_name="eddy",
        full_name="Edmund",
        short_name="Edie",
        username="ediecalendarbot",
        emoji="📅",
        tagline="Events Bot",
        responsibility="Community calendar, event management, meetings, birthdays, schedules, and reminders",
    ),
    "pete": BotIdentity(
        internal_name="pete",
        full_name="Peter",
        short_name="Pete",
        username="petemodbot",
        emoji="🛡️",
        tagline="Safety Bot",
        responsibility="Anti-spam, anti-bot detection, moderation, and community protection",
    ),
    "lusy": BotIdentity(
        internal_name="lusy",
        full_name="Lucy",
        short_name="Lusie",
        username="lusiequizbot",
        emoji="🎯",
        tagline="Games & XP",
        responsibility="Bible quizzes, XP, competitions, and leaderboards",
    ),
}

# The main Mini App is launched primarily through Theo Bot or any registered bot
DEFAULT_MINI_APP_LINK = BOT_REGISTRY["theo"].mini_app_link


def get_bot_identity(internal_name: str) -> BotIdentity:
    if internal_name not in BOT_REGISTRY:
        raise KeyError(f"Unknown bot internal_name: {internal_name}")
    return BOT_REGISTRY[internal_name]
