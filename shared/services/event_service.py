from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


@dataclass(slots=True)
class EventService:
    db: SupabaseGateway

    async def create_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = {"title", "starts_at"}
        missing = required.difference(payload)
        if missing:
            raise ValueError(f"Missing required event fields: {', '.join(sorted(missing))}")
        return await self.db.insert("events", payload)

    async def register_participant(
        self,
        event_id: str,
        user_id: str,
        *,
        status: str = "registered",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self.db.upsert(
            "event_participants",
            {
                "event_id": event_id,
                "user_id": user_id,
                "status": status,
                "metadata": metadata or {},
            },
            on_conflict="event_id,user_id",
        )

    async def mark_attendance(self, event_id: str, user_id: str, attended_at: str) -> dict[str, Any]:
        participant = await self.db.find_one_multi(
            "event_participants",
            {"event_id": event_id, "user_id": user_id},
        )
        if not participant:
            participant = await self.register_participant(event_id, user_id)
        return await self.db.update_by_id(
            "event_participants",
            participant["id"],
            {"status": "attended", "attended_at": attended_at},
        )
