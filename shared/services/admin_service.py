from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


@dataclass(slots=True)
class AdminService:
    """Service dedicated to Admin analytics and community tracking across YouThopiaOS."""
    db: SupabaseGateway

    async def get_global_stats(self) -> dict[str, Any]:
        """Fetch global community metrics from Supabase."""
        try:
            users = await self.db.find_many("users", {})
            user_count = len(users)

            chats = await self.db.find_many("telegram_chats", {"is_active": True})
            group_count = len(chats)

            user_subs = await self.db.find_many("user_subscriptions", {"enabled": True})
            chat_subs = await self.db.find_many("chat_subscriptions", {"enabled": True})

            return {
                "total_users": user_count,
                "active_groups": group_count,
                "user_subscriptions": len(user_subs),
                "chat_subscriptions": len(chat_subs),
            }
        except Exception:
            return {
                "total_users": 0,
                "active_groups": 0,
                "user_subscriptions": 0,
                "chat_subscriptions": 0,
            }

    async def get_bot_breakdown(self) -> dict[str, Any]:
        """Fetch per-bot active chat and subscription breakdown across all 5 bots."""
        bots = ["theo", "lusy", "pete", "eddy", "susy"]
        breakdown = {bot: {"active_chats": 0, "active_subs": 0} for bot in bots}

        try:
            memberships = await self.db.find_many("bot_chat_memberships", {"status": "active"})
            for m in memberships:
                bot_name = (m.get("bot_name") or "").lower()
                if bot_name in breakdown:
                    breakdown[bot_name]["active_chats"] += 1

            chat_subs = await self.db.find_many("chat_subscriptions", {"enabled": True})
            for s in chat_subs:
                bot_name = (s.get("bot_name") or "").lower()
                if bot_name in breakdown:
                    breakdown[bot_name]["active_subs"] += 1

        except Exception:
            pass

        return breakdown

    async def get_active_groups_list(self) -> list[dict[str, Any]]:
        """Fetch all active registered groups in YouThopiaOS."""
        try:
            return await self.db.find_many("telegram_chats", {"is_active": True})
        except Exception:
            return []
