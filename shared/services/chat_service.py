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

    async def _resolve_chat_uuid(self, chat_id_input: str | int) -> str:
        val_str = str(chat_id_input).strip()
        if val_str.lstrip("-").isdigit():
            chat = await self.db.find_one("telegram_chats", "telegram_chat_id", int(val_str))
            if chat and "id" in chat:
                return chat["id"]
            chat = await self.upsert_chat(int(val_str), "group")
            return chat["id"]
        return val_str

    async def set_subscription(
        self,
        bot_name: str,
        chat_id: str | int,
        subscription_type: str,
        *,
        enabled: bool = True,
        schedule: str | None = None,
        timezone: str = "UTC",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._validate_bot_name(bot_name)
        db_chat_id = await self._resolve_chat_uuid(chat_id)
        return await self.db.upsert(
            "chat_subscriptions",
            {
                "bot_name": bot_name,
                "chat_id": db_chat_id,
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

    async def get_active_subscriptions(self, bot_name: str, subscription_type: str) -> list[dict[str, Any]]:
        """Get all active chat subscriptions for a bot and subscription type."""
        self._validate_bot_name(bot_name)
        return await self.db.find_many(
            "chat_subscriptions",
            {"bot_name": bot_name, "subscription_type": subscription_type, "enabled": True}
        )

    async def get_chat_by_id(self, chat_id: str) -> dict[str, Any]:
        """Get chat details by its internal DB UUID."""
        return await self.db.get_by_id("telegram_chats", chat_id)

    async def get_bot_settings(self, bot_name: str, chat_id: str) -> dict[str, Any]:
        """Fetch settings for a bot in a specific chat, defaulting to {}."""
        settings_row = await self.db.find_one_multi(
            "chat_bot_settings",
            {"bot_name": bot_name, "chat_id": chat_id}
        )
        if not settings_row:
            return {}
        return settings_row.get("settings") or {}

    async def get_subscription(
        self, bot_name: str, chat_id: str | int, subscription_type: str
    ) -> dict[str, Any] | None:
        """Fetch subscription record for a bot in a specific chat."""
        self._validate_bot_name(bot_name)
        db_chat_id = await self._resolve_chat_uuid(chat_id)
        return await self.db.find_one_multi(
            "chat_subscriptions",
            {"chat_id": db_chat_id, "bot_name": bot_name, "subscription_type": subscription_type}
        )

    def _validate_bot_name(self, bot_name: str) -> None:
        if bot_name not in VALID_BOT_NAMES:
            raise ValueError(f"Invalid bot name: {bot_name}")
