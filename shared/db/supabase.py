from __future__ import annotations

import asyncio
from dataclasses import dataclass
import time
from typing import Any

from supabase import Client, create_client


class SupabaseNotConfiguredError(RuntimeError):
    pass


def _execute_with_retry(query_fn, retries: int = 3):
    """Executes a Supabase query function with 3 retries in case of transient network/SSL timeouts."""
    for attempt in range(retries):
        try:
            return query_fn()
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(0.2)


@dataclass(slots=True)
class SupabaseGateway:
    url: str
    key: str
    client: Client | None = None

    def connect(self) -> "SupabaseGateway":
        if not self.url or not self.key:
            raise SupabaseNotConfiguredError("SUPABASE_URL and SUPABASE_KEY are required.")
        self.client = create_client(self.url, self.key)
        return self

    def _client(self) -> Client:
        if self.client is None:
            self.connect()
        if self.client is None:
            raise SupabaseNotConfiguredError("Supabase client is not available.")
        return self.client

    async def insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            response = _execute_with_retry(lambda: self._client().table(table).insert(payload).execute())
            return _first(response.data)

        return await asyncio.to_thread(run)

    async def upsert(self, table: str, payload: dict[str, Any], *, on_conflict: str | None = None) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            query = self._client().table(table).upsert(payload, on_conflict=on_conflict)
            response = _execute_with_retry(lambda: query.execute())
            return _first(response.data)

        return await asyncio.to_thread(run)

    async def get_by_id(self, table: str, record_id: str) -> dict[str, Any]:
        found = await self.find_one(table, "id", record_id)
        if not found:
            raise LookupError(f"{table} record not found: {record_id}")
        return found

    async def find_one(self, table: str, column: str, value: Any) -> dict[str, Any] | None:
        return await self.find_one_multi(table, {column: value})

    async def find_one_multi(self, table: str, filters: dict[str, Any]) -> dict[str, Any] | None:
        def run() -> dict[str, Any] | None:
            query = self._client().table(table).select("*")
            for column, value in filters.items():
                query = query.eq(column, value)
            response = _execute_with_retry(lambda: query.limit(1).execute())
            return response.data[0] if response.data else None

        return await asyncio.to_thread(run)

    async def find_many(self, table: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        def run() -> list[dict[str, Any]]:
            query = self._client().table(table).select("*")
            for column, value in filters.items():
                query = query.eq(column, value)
            response = _execute_with_retry(lambda: query.execute())
            return response.data or []

        return await asyncio.to_thread(run)

    async def update_by_id(self, table: str, record_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            query = self._client().table(table).update(updates).eq("id", record_id)
            response = _execute_with_retry(lambda: query.execute())
            return _first(response.data)

        return await asyncio.to_thread(run)


def _first(data: list[dict[str, Any]] | None) -> dict[str, Any]:
    if not data:
        return {}
    return data[0]
