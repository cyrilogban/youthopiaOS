from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


VALID_BOT_NAMES = {"theo", "lusy", "pete", "eddy", "susy"}
VALID_MEMBERSHIP_STATUSES = {"active", "left", "kicked", "disabled"}


@dataclass(slots=True)
class ChatService:
    db: SupabaseGateway

    async def upsert_chat(
        self,
        telegram_chat_id: int,
        chat_type: str,
        *,
        title: str | None = None,
        username: str | None = None,
        is_active: bool = True,
        is_official: bool = False,
    ) -> dict[str, Any]:
        return await self.db.upsert(
            "telegram_chats",
            {
                "telegram_chat_id": int(telegram_chat_id),
                "chat_type": chat_type,
                "title": title,
                "username": username,
                "is_active": is_active,
                "is_official": is_official,
            },
            on_conflict="telegram_chat_id",
        )

    async def mark_bot_active(
        self,
        bot_name: str,
        chat_id: str,
        *,
        enabled: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._validate_bot_name(bot_name)
        return await self.db.upsert(
            "bot_chat_memberships",
            {
                "bot_name": bot_name,
                "chat_id": chat_id,
                "status": "active",
                "enabled": enabled,
                "left_at": None,
                "metadata": metadata or {},
            },
            on_conflict="chat_id,bot_name",
        )

    async def mark_bot_status(
        self,
        bot_name: str,
        chat_id: str,
        status: str,
        *,
        enabled: bool | None = None,
        left_at: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._validate_bot_name(bot_name)
        if status not in VALID_MEMBERSHIP_STATUSES:
            raise ValueError(f"Invalid bot chat membership status: {status}")

        payload: dict[str, Any] = {
            "bot_name": bot_name,
            "chat_id": chat_id,
            "status": status,
            "metadata": metadata or {},
        }
        if enabled is not None:
            payload["enabled"] = enabled
        if left_at is not None:
            payload["left_at"] = left_at

        return await self.db.upsert("bot_chat_memberships", payload, on_conflict="chat_id,bot_name")

    async def set_bot_settings(
        self,
        bot_name: str,
        chat_id: str,
        settings: dict[str, Any],
    ) -> dict[str, Any]:
        self._validate_bot_name(bot_name)
        return await self.db.upsert(
            "chat_bot_settings",
            {"bot_name": bot_name, "chat_id": chat_id, "settings": settings},
            on_conflict="chat_id,bot_name",
        )

    async def set_subscription(
        self,
        bot_name: str,
        chat_id: str,
        subscription_type: str,
        *,
        enabled: bool = True,
        schedule: str | None = None,
        timezone: str = "UTC",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._validate_bot_name(bot_name)
        return await self.db.upsert(
            "chat_subscriptions",
            {
                "bot_name": bot_name,
                "chat_id": chat_id,
                "subscription_type": subscription_type,
                "enabled": enabled,
                "schedule": schedule,
                "timezone": timezone,
                "metadata": metadata or {},
            },
            on_conflict="chat_id,bot_name,subscription_type",
        )

    async def get_enabled_bot_chats(self, bot_name: str) -> list[dict[str, Any]]:
        self._validate_bot_name(bot_name)
        return await self.db.find_many(
            "bot_chat_memberships",
            {"bot_name": bot_name, "status": "active", "enabled": True},
        )

    def _validate_bot_name(self, bot_name: str) -> None:
        if bot_name not in VALID_BOT_NAMES:
            raise ValueError(f"Invalid bot name: {bot_name}")
