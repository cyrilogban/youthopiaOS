import logging
from typing import Any
from dataclasses import dataclass
from shared.db.supabase import SupabaseGateway

logger = logging.getLogger(__name__)

@dataclass
class ModerationService:
    """Handles business logic for Pete's moderation and trust score system."""
    db: SupabaseGateway
    
    async def record_action(
        self,
        offender_uuid: str,
        chat_uuid: str,
        moderator_uuid: str,
        action_type: str,
        reason: str | None = None,
        trust_delta: int = 0
    ) -> dict[str, Any]:
        """Records a moderation action and actively penalizes the user's global Trust Score."""
        
        # 1. Log the action permanently for audit trails
        action_record = await self.db.insert(
            "moderation_actions",
            {
                "user_id": offender_uuid,
                "chat_id": chat_uuid,
                "moderator_user_id": moderator_uuid,
                "action_type": action_type,
                "reason": reason,
                "trust_delta": trust_delta
            }
        )
        
        # 2. Execute the Global Trust Penalty
        if trust_delta != 0:
            user = await self.db.get_by_id("users", offender_uuid)
            current_score = user.get("trust_score", 100)
            new_score = max(0, current_score + trust_delta)  # Floor at 0
            
            await self.db.update_by_id("users", offender_uuid, {"trust_score": new_score})
            logger.info(f"User {offender_uuid} trust score changed by {trust_delta}. New score: {new_score}")
            
        return action_record
        
    async def get_user_warnings_count(self, offender_uuid: str, chat_uuid: str) -> int:
        """Counts how many warnings a user has received in a specific chat."""
        import asyncio
        def run() -> int:
            response = (
                self.db._client()
                .table("moderation_actions")
                .select("id", count="exact")
                .eq("user_id", offender_uuid)
                .eq("chat_id", chat_uuid)
                .eq("action_type", "warn")
                .execute()
            )
            return response.count or 0
        return await asyncio.to_thread(run)
