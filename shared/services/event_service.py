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

    async def get_user_upcoming_events(self, telegram_id: int) -> list[dict[str, Any]] | None:
        """Fetch upcoming events that the user RSVP'd 'coming' to."""
        import asyncio
        # 1. Lookup the official UUID in telegram_accounts
        account = await self.db.find_one("telegram_accounts", "telegram_id", int(telegram_id))
        if not account:
            return None
        user_uuid = account["user_id"]
        
        # 2. Get all RSVPs where status is 'coming'
        def run() -> list[dict[str, Any]]:
            participant_resp = (
                self.db._client()
                .table("event_participants")
                .select("event_id")
                .eq("user_id", user_uuid)
                .eq("status", "coming")
                .execute()
            )
            event_ids = [p["event_id"] for p in (participant_resp.data or [])]
            if not event_ids:
                return []
                
            events_resp = (
                self.db._client()
                .table("events")
                .select("title, starts_at")
                .in_("id", event_ids)
                .execute()
            )
            return events_resp.data or []
            
        return await asyncio.to_thread(run)

    async def find_event_by_title_and_date(self, title: str, start_date_iso: str) -> dict[str, Any] | None:
        """Find an event matching title and created after start_date_iso."""
        import asyncio
        def run():
            response = (
                self.db._client()
                .table("events")
                .select("id")
                .eq("title", title)
                .gte("created_at", start_date_iso)
                .execute()
            )
            return response.data[0] if response.data else None
        return await asyncio.to_thread(run)

    async def get_event_participants_metadata(self, event_id: str, status: str = "coming") -> list[dict[str, Any]]:
        """Fetch metadata for participants matching event_id and status."""
        import asyncio
        def run():
            response = (
                self.db._client()
                .table("event_participants")
                .select("metadata")
                .eq("event_id", event_id)
                .eq("status", status)
                .execute()
            )
            return response.data or []
        return await asyncio.to_thread(run)
