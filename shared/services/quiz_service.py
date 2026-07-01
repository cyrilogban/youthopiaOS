from __future__ import annotations

import asyncio
import datetime
from dataclasses import dataclass
from typing import Any

from shared.db.supabase import SupabaseGateway


@dataclass(slots=True)
class QuizService:
    db: SupabaseGateway

    async def get_questions_by_difficulty(self, difficulty: str) -> list[dict[str, Any]]:
        """Fetch active multiple choice questions for a specific difficulty."""
        return await self.db.find_many(
            "lusy_questions",
            {"game_type": "multiple_choice", "difficulty": difficulty, "is_active": True}
        )

    async def get_game_history(self, user_id: str) -> list[dict[str, Any]]:
        """Fetch the user's game/quiz play history."""
        return await self.db.find_many("lusy_game_history", {"user_id": user_id})

    async def track_private_poll(
        self, user_id: str, poll_id: str, question_id: str, base_xp: int
    ) -> dict[str, Any]:
        """Save active private poll state for deep polling resolution."""
        return await self.db.upsert(
            "bot_user_state",
            {
                "user_id": user_id,
                "bot_name": "lusy_poll_tracking",
                "state": {"poll_id": poll_id, "question_id": question_id, "base_xp": base_xp},
            },
            on_conflict="user_id, bot_name",
        )

    async def get_question_by_id(self, question_id: str) -> dict[str, Any] | None:
        """Fetch a specific question by its ID."""
        return await self.db.find_one("lusy_questions", "id", question_id)

    async def save_game_result(
        self, user_id: str, question_id: str, is_correct: bool, xp_earned: int
    ) -> dict[str, Any]:
        """Insert a quiz play result into history."""
        return await self.db.insert(
            "lusy_game_history",
            {
                "user_id": user_id,
                "question_id": question_id,
                "is_correct": is_correct,
                "xp_earned": xp_earned,
                "answered_at": datetime.datetime.utcnow().isoformat(),
            },
        )

    async def clear_private_poll_tracking(self, user_id: str) -> None:
        """Remove active poll mapping state."""
        def run():
            self.db.client.table("bot_user_state").delete().eq("user_id", user_id).eq(
                "bot_name", "lusy_poll_tracking"
            ).execute()

        await asyncio.to_thread(run)
