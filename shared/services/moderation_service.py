from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


@dataclass(slots=True)
class ModerationService:
    db: SupabaseGateway

    async def record_action(
        self,
        user_id: str,
        action_type: str,
        *,
        chat_id: str | None = None,
        moderator_user_id: str | None = None,
        reason: str | None = None,
        trust_delta: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        action = await self.db.insert(
            "moderation_actions",
            {
                "user_id": user_id,
                "chat_id": chat_id,
                "moderator_user_id": moderator_user_id,
                "action_type": action_type,
                "reason": reason,
                "trust_delta": trust_delta,
                "metadata": metadata or {},
            },
        )

        if trust_delta:
            user = await self.db.get_by_id("users", user_id)
            trust_score = min(100, max(0, int(user.get("trust_score", 100)) + trust_delta))
            await self.db.update_by_id("users", user_id, {"trust_score": trust_score})

        return action

    async def get_user_warnings_count(self, user_id: str, chat_id: str | None = None) -> int:
        """Counts how many warnings a user has received. If chat_id is provided, filters by chat."""
        import asyncio
        def run() -> int:
            query = (
                self.db._client()
                .table("moderation_actions")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("action_type", "warn")
            )
            if chat_id:
                query = query.eq("chat_id", chat_id)
            response = query.execute()
            return response.count or 0
        return await asyncio.to_thread(run)
