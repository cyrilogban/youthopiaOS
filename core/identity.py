from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.services.user_service import UserService


@dataclass(slots=True)
class IdentityResolver:
    users: UserService

    async def resolve_telegram_user(self, telegram_user: Any) -> dict[str, Any]:
        telegram_id = getattr(telegram_user, "id", None)
        if telegram_id is None and isinstance(telegram_user, dict):
            telegram_id = telegram_user.get("id") or telegram_user.get("telegram_id")
        if telegram_id is None:
            raise ValueError("Telegram user payload must include an id.")

        payload = {
            "telegram_id": int(telegram_id),
            "username": _get(telegram_user, "username"),
            "first_name": _get(telegram_user, "first_name"),
            "last_name": _get(telegram_user, "last_name"),
            "is_bot": bool(_get(telegram_user, "is_bot", False)),
        }
        return await self.users.get_or_create_from_telegram(payload)


def _get(source: Any, key: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)
