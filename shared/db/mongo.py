from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from pymongo import MongoClient


@dataclass(slots=True)
class TelemetryMongoGateway:
    uri: str
    database_name: str = "youthopiaos"
    server_selection_timeout_ms: int = 2000
    client: MongoClient | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.uri)

    def connect(self) -> "TelemetryMongoGateway":
        if self.uri and self.client is None:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=self.server_selection_timeout_ms,
            )
        return self

    async def log_event(
        self,
        event_name: str,
        *,
        bot_name: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return

        def run() -> None:
            self.connect()
            if self.client is None:
                return
            self.client[self.database_name]["telemetry_events"].insert_one(
                {
                    "event_name": event_name,
                    "bot_name": bot_name,
                    "payload": payload or {},
                    "created_at": datetime.now(UTC),
                }
            )

        try:
            await asyncio.to_thread(run)
        except Exception:
            # Telemetry must never break authoritative Supabase flows.
            return
