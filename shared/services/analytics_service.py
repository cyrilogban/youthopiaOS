from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.db.mongo import TelemetryMongoGateway
from shared.db.supabase import SupabaseGateway


@dataclass(slots=True)
class AnalyticsService:
    db: SupabaseGateway
    telemetry: TelemetryMongoGateway

    async def track(
        self,
        event_name: str,
        *,
        user_id: str | None = None,
        bot_name: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "user_id": user_id,
            "bot_name": bot_name,
            "event_name": event_name,
            "properties": properties or {},
        }
        await self.db.insert("analytics_events", payload)
        await self.telemetry.log_event(event_name, bot_name=bot_name, payload=payload)
