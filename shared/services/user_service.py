from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


@dataclass(slots=True)
class UserService:
    db: SupabaseGateway

    async def get_user(self, user_id: str) -> dict[str, Any]:
        return await self.db.get_by_id("users", user_id)

    async def get_by_telegram_id(self, telegram_id: int) -> dict[str, Any] | None:
        account = await self.db.find_one("telegram_accounts", "telegram_id", int(telegram_id))
        if not account:
            return None
        return await self.db.get_by_id("users", account["user_id"])

    async def create_user(self, *, display_name: str | None = None) -> dict[str, Any]:
        return await self.db.insert("users", {"display_name": display_name})

    async def get_or_create_from_telegram(self, telegram: dict[str, Any]) -> dict[str, Any]:
        telegram_id = int(telegram["telegram_id"])
        account = await self.db.find_one("telegram_accounts", "telegram_id", telegram_id)
        if account:
            await self.db.update_by_id(
                "telegram_accounts",
                account["id"],
                {
                    "username": telegram.get("username"),
                    "first_name": telegram.get("first_name"),
                    "last_name": telegram.get("last_name"),
                    "is_bot": bool(telegram.get("is_bot", False)),
                },
            )
            return await self.db.get_by_id("users", account["user_id"])

        display_name = telegram.get("first_name") or telegram.get("username")
        user = await self.create_user(display_name=display_name)
        await self.db.insert(
            "telegram_accounts",
            {
                "user_id": user["id"],
                "telegram_id": telegram_id,
                "username": telegram.get("username"),
                "first_name": telegram.get("first_name"),
                "last_name": telegram.get("last_name"),
                "is_bot": bool(telegram.get("is_bot", False)),
            },
        )
        await self.db.upsert(
            "user_levels",
            {"user_id": user["id"], "total_xp": 0, "level": 1},
            on_conflict="user_id",
        )
        return user

    async def set_engagement_level(self, user_id: str, level: str) -> None:
        await self.db.update_by_id("users", user_id, {"engagement_level": level})

    async def set_subscription(
        self,
        user_id: str,
        bot_name: str,
        subscription_type: str,
        *,
        enabled: bool = True,
        schedule: str | None = None,
        timezone: str = "UTC",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self.db.upsert(
            "user_subscriptions",
            {
                "user_id": user_id,
                "bot_name": bot_name,
                "subscription_type": subscription_type,
                "enabled": enabled,
                "schedule": schedule,
                "timezone": timezone,
                "metadata": metadata or {},
            },
            on_conflict="user_id,bot_name,subscription_type",
        )


_default_service: UserService | None = None


def configure(service: UserService) -> None:
    global _default_service
    _default_service = service


def _service() -> UserService:
    if _default_service is None:
        raise RuntimeError("UserService has not been configured.")
    return _default_service


async def get_user(user_id: str) -> dict[str, Any]:
    return await _service().get_user(user_id)


async def create_user(*, display_name: str | None = None, **_: Any) -> dict[str, Any]:
    return await _service().create_user(display_name=display_name)


async def get_or_create_from_telegram(telegram: dict[str, Any]) -> dict[str, Any]:
    return await _service().get_or_create_from_telegram(telegram)


async def set_engagement_level(user_id: str, level: str) -> None:
    await _service().set_engagement_level(user_id, level)
