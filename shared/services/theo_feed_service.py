from __future__ import annotations

import asyncio
from typing import Any
from shared.db.supabase import SupabaseGateway


class TheoFeedService:
    def __init__(self, db: SupabaseGateway):
        self.db = db

    async def get_featured_verses(self, limit: int = 10) -> list[dict[str, Any]]:
        """Fetch active admin-curated featured verses from Supabase."""
        def run():
            response = (
                self.db._client()
                .table("featured_verses")
                .select("*")
                .eq("is_active", True)
                .order("scheduled_date", desc=True)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []

        return await asyncio.to_thread(run)

    async def get_saved_verses(self, telegram_id: int) -> list[dict[str, Any]]:
        """Fetch bookmarked verses for a user from Supabase."""
        def run():
            response = (
                self.db._client()
                .table("saved_verses")
                .select("*")
                .eq("user_id", telegram_id)
                .order("saved_at", desc=True)
                .execute()
            )
            return response.data or []

        return await asyncio.to_thread(run)

    async def save_verse(
        self, telegram_id: int, verse_reference: str, verse_text: str, translation: str = "KJV"
    ) -> dict[str, Any]:
        """Save/bookmark a verse for a user in Supabase."""
        def run():
            # Check if already saved
            existing = (
                self.db._client()
                .table("saved_verses")
                .select("*")
                .eq("user_id", telegram_id)
                .eq("verse_reference", verse_reference)
                .limit(1)
                .execute()
            )
            if existing.data:
                return existing.data[0]

            response = (
                self.db._client()
                .table("saved_verses")
                .insert({
                    "user_id": telegram_id,
                    "verse_reference": verse_reference,
                    "verse_text": verse_text,
                    "translation": translation,
                })
                .execute()
            )
            return response.data[0] if response.data else {}

        return await asyncio.to_thread(run)

    async def unsave_verse(self, telegram_id: int, verse_reference: str) -> bool:
        """Remove a saved verse for a user."""
        def run():
            response = (
                self.db._client()
                .table("saved_verses")
                .delete()
                .eq("user_id", telegram_id)
                .eq("verse_reference", verse_reference)
                .execute()
            )
            return bool(response.data)

        return await asyncio.to_thread(run)

    async def get_user_likes(self, telegram_id: int) -> list[str]:
        """Fetch list of verse references liked by the user."""
        def run():
            response = (
                self.db._client()
                .table("likes")
                .select("verse_reference")
                .eq("user_id", telegram_id)
                .execute()
            )
            return [row["verse_reference"] for row in (response.data or [])]

        return await asyncio.to_thread(run)

    async def toggle_like(self, telegram_id: int, verse_reference: str) -> bool:
        """Toggle like status on a verse. Returns True if liked, False if unliked."""
        def run():
            client = self.db._client()
            existing = (
                client.table("likes")
                .select("id")
                .eq("user_id", telegram_id)
                .eq("verse_reference", verse_reference)
                .limit(1)
                .execute()
            )
            if existing.data:
                client.table("likes").delete().eq("user_id", telegram_id).eq("verse_reference", verse_reference).execute()
                return False
            else:
                client.table("likes").insert({
                    "user_id": telegram_id,
                    "verse_reference": verse_reference,
                }).execute()
                return True

        return await asyncio.to_thread(run)

    async def log_share_event(self, user_uuid: str, verse_reference: str) -> dict[str, Any]:
        """Log a share event in analytics_events in Supabase."""
        def run():
            response = (
                self.db._client()
                .table("analytics_events")
                .insert({
                    "user_id": user_uuid,
                    "bot_name": "theo",
                    "event_name": "verse_shared",
                    "properties": {"verse_reference": verse_reference},
                })
                .execute()
            )
            return response.data[0] if response.data else {}

        return await asyncio.to_thread(run)
