"""Gateway data models.

Pydantic models for the FastAPI trust boundary. The bots use dataclasses/dicts,
but this is a FastAPI service — Pydantic is the native idiom here: it validates
untrusted input on parse and serializes responses for free.

`TelegramUser` mirrors Telegram's WebApp `user` object field-for-field (native
names), so a parsed instance drops straight into core.identity.IdentityResolver
at Module 4 (it reads .id / .first_name / ... via getattr) with no adapter.
"""
from __future__ import annotations

from urllib.parse import parse_qsl

from pydantic import BaseModel, ValidationError


class TelegramUser(BaseModel):
    """The user Telegram embeds in initData (its WebAppUser object)."""

    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None
    photo_url: str | None = None

    @classmethod
    def from_raw_init_data(cls, raw_init_data: str) -> "TelegramUser | None":
        """Extract and validate the `user` field out of raw initData.

        Returns a validated TelegramUser, or None if the field is absent or
        malformed (e.g. missing id) — parse, don't trust.
        """
        pairs = dict(parse_qsl(raw_init_data, keep_blank_values=True))
        user_json = pairs.get("user")
        if not user_json:
            return None
        try:
            return cls.model_validate_json(user_json)
        except ValidationError:
            return None
