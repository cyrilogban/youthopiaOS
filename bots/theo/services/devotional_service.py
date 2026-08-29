from typing import Any, Optional
import aiohttp
import asyncio
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from shared.db.supabase import SupabaseGateway

WAT_TZ = ZoneInfo("Africa/Lagos")

FALLBACK_VOTD = [
    {"reference": "John 14:27", "category": "peace"},
    {"reference": "Philippians 4:6", "category": "peace"},
    {"reference": "Hebrews 11:1", "category": "faith"},
    {"reference": "2 Corinthians 5:7", "category": "faith"},
    {"reference": "Jeremiah 29:11", "category": "hope"},
    {"reference": "Psalm 42:11", "category": "hope"},
    {"reference": "1 Corinthians 13:4", "category": "love"},
    {"reference": "John 3:16", "category": "love"},
    {"reference": "Nehemiah 8:10", "category": "joy"},
    {"reference": "Psalm 16:11", "category": "joy"},
    {"reference": "Ephesians 4:32", "category": "forgiveness"},
    {"reference": "James 1:3", "category": "patience"},
]


class VOTDService:
    """Service to handle fetching the Verse of the Day reference from Supabase
    and the actual verse text from an external Bible API.
    """

    def __init__(self, db: SupabaseGateway):
        self.db = db

    async def get_todays_reference(self) -> Optional[dict]:
        """Fetches today's scheduled verse reference from Supabase (Africa/Lagos WAT date)."""
        today_str = datetime.now(WAT_TZ).date().isoformat()

        def run() -> Optional[dict]:
            try:
                response = (
                    self.db._client()
                    .table("verse_of_the_day")
                    .select("*")
                    .eq("scheduled_date", today_str)
                    .execute()
                )
                if response.data:
                    return response.data[0]
            except Exception:
                pass
            
            # Rotational fallback so Theo never misses a day even if table has no entry
            day_of_year = datetime.now(WAT_TZ).timetuple().tm_yday
            fallback = FALLBACK_VOTD[day_of_year % len(FALLBACK_VOTD)]
            return {"reference": fallback["reference"], "category": fallback["category"], "scheduled_date": today_str}

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
                        verses = data.get("verses", [])
                        
                        if not verses:
                            return data.get("text", "").strip()
                            
                        if len(verses) == 1:
                            return verses[0].get("text", "").strip()
                            
                        # Professional formatting for multiple verses
                        formatted_lines = []
                        for v in verses:
                            verse_num = v.get("verse")
                            verse_text = v.get("text", "").strip()
                            formatted_lines.append(f"[{verse_num}] {verse_text}")
                            
                        return "\n".join(formatted_lines)
                    else:
                        return None
            except Exception:
                return None
