from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from shared.db.supabase import SupabaseGateway, _execute_with_retry

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AdminService:
    """Service dedicated to Admin analytics and community tracking across YouThopiaOS."""
    db: SupabaseGateway

    async def get_active_users_count(self, days: int = 30) -> int:
        """Fetch count of distinct active users within the last N days (e.g. 30 for MAU, 1 for DAU)."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        try:
            def run() -> int:
                res = _execute_with_retry(
                    lambda: (
                        self.db._client()
                        .table("telegram_accounts")
                        .select("user_id", count="exact", head=True)
                        .gte("last_seen_at", cutoff)
                        .execute()
                    )
                )
                return res.count if res and res.count is not None else 0

            return await asyncio.to_thread(run)
        except Exception as e:
            logger.warning(f"Failed to fetch active users count ({days}d): {e}")
            return 0

    async def get_global_stats(self) -> dict[str, Any]:
        """Fetch global community metrics from Supabase using zero-payload count headers."""
        now = datetime.now(timezone.utc)
        cutoff_30d = (now - timedelta(days=30)).isoformat()
        cutoff_24h = (now - timedelta(days=1)).isoformat()

        def fetch_counts() -> dict[str, Any]:
            client = self.db._client()

            # 1. Total Registered Users
            total_users_res = _execute_with_retry(
                lambda: client.table("users").select("id", count="exact", head=True).execute()
            )
            total_users = total_users_res.count if total_users_res and total_users_res.count is not None else 0

            # 2. Monthly Active Users (MAU - 30 days)
            mau_res = _execute_with_retry(
                lambda: client.table("telegram_accounts")
                .select("user_id", count="exact", head=True)
                .gte("last_seen_at", cutoff_30d)
                .execute()
            )
            mau = mau_res.count if mau_res and mau_res.count is not None else 0

            # 3. Daily Active Users (DAU - 24 hours)
            dau_res = _execute_with_retry(
                lambda: client.table("telegram_accounts")
                .select("user_id", count="exact", head=True)
                .gte("last_seen_at", cutoff_24h)
                .execute()
            )
            dau = dau_res.count if dau_res and dau_res.count is not None else 0

            # 4. Active Groups
            chats_res = _execute_with_retry(
                lambda: client.table("telegram_chats")
                .select("id", count="exact", head=True)
                .eq("is_active", True)
                .execute()
            )
            group_count = chats_res.count if chats_res and chats_res.count is not None else 0

            # 5. User Subscriptions
            user_subs_res = _execute_with_retry(
                lambda: client.table("user_subscriptions")
                .select("id", count="exact", head=True)
                .eq("enabled", True)
                .execute()
            )
            user_subs_count = user_subs_res.count if user_subs_res and user_subs_res.count is not None else 0

            # 6. Chat Subscriptions
            chat_subs_res = _execute_with_retry(
                lambda: client.table("chat_subscriptions")
                .select("id", count="exact", head=True)
                .eq("enabled", True)
                .execute()
            )
            chat_subs_count = chat_subs_res.count if chat_subs_res and chat_subs_res.count is not None else 0

            return {
                "total_users": total_users,
                "mau": mau,
                "dau": dau,
                "active_groups": group_count,
                "user_subscriptions": user_subs_count,
                "chat_subscriptions": chat_subs_count,
            }

        try:
            return await asyncio.to_thread(fetch_counts)
        except Exception as e:
            logger.error(f"Failed to fetch global stats: {e}")
            return {
                "total_users": 0,
                "mau": 0,
                "dau": 0,
                "active_groups": 0,
                "user_subscriptions": 0,
                "chat_subscriptions": 0,
            }

    async def get_bot_breakdown(self) -> dict[str, Any]:
        """Fetch per-bot active chat and subscription breakdown across all 5 bots."""
        bots = ["theo", "lusy", "pete", "eddy", "susy"]
        breakdown = {bot: {"active_chats": 0, "active_subs": 0} for bot in bots}

        try:
            memberships = await self.db.find_many("bot_chat_memberships", {"status": "active"})
            for m in memberships:
                bot_name = (m.get("bot_name") or "").lower()
                if bot_name in breakdown:
                    breakdown[bot_name]["active_chats"] += 1

            chat_subs = await self.db.find_many("chat_subscriptions", {"enabled": True})
            for s in chat_subs:
                bot_name = (s.get("bot_name") or "").lower()
                if bot_name in breakdown:
                    breakdown[bot_name]["active_subs"] += 1

        except Exception as e:
            logger.warning(f"Failed to fetch bot breakdown: {e}")

        return breakdown

    async def get_active_groups_list(self) -> list[dict[str, Any]]:
        """Fetch all active registered groups in YouThopiaOS."""
        try:
            return await self.db.find_many("telegram_chats", {"is_active": True})
        except Exception as e:
            logger.warning(f"Failed to fetch active groups list: {e}")
            return []
