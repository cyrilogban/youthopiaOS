import aiohttp
import asyncio
from datetime import date
from typing import Optional

from shared.db.supabase import SupabaseGateway


class VOTDService:
    """Service to handle fetching the Verse of the Day reference from Supabase
    and the actual verse text from an external Bible API.
    """

    def __init__(self, db: SupabaseGateway):
        self.db = db

    async def get_todays_reference(self) -> Optional[dict]:
        """Fetches today's scheduled verse reference from Supabase."""
        today_str = date.today().isoformat()

        def run() -> Optional[dict]:
            response = (
                self.db._client()
                .table("verse_of_the_day")
                .select("*")
                .eq("scheduled_date", today_str)
                .execute()
            )
            return response.data[0] if response.data else None

        return await asyncio.to_thread(run)

    async def fetch_bible_text(self, reference: str, translation: str = "kjv") -> Optional[str]:
        """Fetches the actual text of the verse from bible-api.com."""
        # bible-api.com supports standard references like "John 3:16"
        url = f"https://bible-api.com/{reference}?translation={translation}"
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("text", "").strip()
                    else:
                        return None
            except Exception:
                return None
