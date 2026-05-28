from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


def calculate_level(total_xp: int) -> int:
    return max(1, (max(total_xp, 0) // 100) + 1)


@dataclass(slots=True)
class XPService:
    db: SupabaseGateway

    async def award_xp(
        self,
        user_id: str,
        amount: int,
        bot_name: str,
        source: str,
        *,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if amount <= 0:
            raise ValueError("XP amount must be greater than zero.")

        if idempotency_key:
            existing = await self.db.find_one("xp_transactions", "idempotency_key", idempotency_key)
            if existing:
                return existing

        transaction = await self.db.insert(
            "xp_transactions",
            {
                "user_id": user_id,
                "amount": amount,
                "bot_name": bot_name,
                "source": source,
                "idempotency_key": idempotency_key,
                "metadata": metadata or {},
            },
        )

        user = await self.db.get_by_id("users", user_id)
        total_xp = int(user.get("total_xp", 0)) + amount
        level = calculate_level(total_xp)

        await self.db.update_by_id("users", user_id, {"total_xp": total_xp, "level": level})
        await self.db.upsert(
            "user_levels",
            {"user_id": user_id, "total_xp": total_xp, "level": level},
            on_conflict="user_id",
        )
        return transaction

    async def get_level(self, user_id: str) -> dict[str, Any]:
        user = await self.db.get_by_id("users", user_id)
        total_xp = int(user.get("total_xp", 0))
        return {"user_id": user_id, "total_xp": total_xp, "level": calculate_level(total_xp)}
