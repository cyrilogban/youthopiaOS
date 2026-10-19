from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from shared.db.supabase import SupabaseGateway
from shared.services.rank_service import RankService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RankScoreInputs:
    """Normalized inputs feeding the holistic cross-bot rank score."""

    trust_score: int = 100
    total_xp: int = 0
    quizzes_played: int = 0
    correct_answers: int = 0
    saved_verses: int = 0
    votd_subscribed: bool = False
    reading_streak: int = 0
    rsvps: int = 0
    events_attended: int = 0
    onboarded: bool = False
    days_in_community: int = 0


def compute_rank_score(inputs: RankScoreInputs) -> int:
    """Pure cross-bot rank score (Decision 7). Auto ceiling is applied later by RankService."""
    # Theo: saved verses, VOTD subscription, reading streak
    theo = (
        min(max(inputs.saved_verses, 0) * 5, 150)
        + (25 if inputs.votd_subscribed else 0)
        + min(max(inputs.reading_streak, 0) * 2, 100)
    )

    # Lusie: quiz XP, quizzes played, accuracy
    accuracy = (inputs.correct_answers / inputs.quizzes_played * 100) if inputs.quizzes_played > 0 else 0.0
    lusie = (
        min(max(inputs.total_xp, 0) // 10, 400)
        + min(max(inputs.quizzes_played, 0) * 2, 100)
        + min(int(accuracy * 1.5), 150)
    )

    # Pete: trust score
    pete = max(0, min(inputs.trust_score, 100))

    # Edie: event RSVPs and attendance
    edie = min(max(inputs.rsvps, 0) * 10, 150) + min(max(inputs.events_attended, 0) * 25, 250)

    # Susie: onboarding completion
    susie = 100 if inputs.onboarded else 0

    # Time in community
    time_bonus = min(int(max(inputs.days_in_community, 0) * 0.5), 500)

    return theo + lusie + pete + edie + susie + time_bonus


def _days_since(created_at: Any, now: datetime) -> int:
    if not created_at:
        return 0
    try:
        dt = created_at
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0, (now - dt).days)
    except Exception:
        return 0


@dataclass(slots=True)
class RankScoreService:
    """Recomputes holistic ``rank_score`` for members and stores the resolved rank."""

    db: SupabaseGateway

    async def recompute_all(self) -> int:
        """Recompute rank_score + resolved rank for every user. Returns rows updated."""
        now = datetime.now(timezone.utc)
        users = await self._safe(self._fetch_users) or []
        if not users:
            return 0

        saved = await self._safe(self._count_rows, "user_saved_verses", "user_id") or {}
        quiz = await self._safe(self._quiz_counts) or {}
        events = await self._safe(self._event_counts) or {}
        subscribed = await self._safe(self._theo_subscribers) or set()
        orientation = await self._safe(self._orientation_completed) or set()

        updated = 0
        for user in users:
            uid = user.get("id")
            if not uid:
                continue

            played, correct = quiz.get(uid, (0, 0))
            rsvps, attended = events.get(uid, (0, 0))
            onboarded = user.get("engagement_level") == "onboarded" or uid in orientation

            score = compute_rank_score(RankScoreInputs(
                trust_score=int(user.get("trust_score") or 100),
                total_xp=int(user.get("total_xp") or 0),
                quizzes_played=played,
                correct_answers=correct,
                saved_verses=saved.get(uid, 0),
                votd_subscribed=uid in subscribed,
                reading_streak=int(user.get("reading_streak") or 0),
                rsvps=rsvps,
                events_attended=attended,
                onboarded=onboarded,
                days_in_community=_days_since(user.get("created_at"), now),
            ))

            rank = RankService.resolve_rank(score, user.get("manual_rank_id"))

            try:
                await self.db.update_by_id("users", uid, {
                    "rank_score": score,
                    "rank_id": rank.id,
                    "rank_title": rank.title,
                    "rank_tier": rank.tier,
                    "rank_badge_color": rank.bg_color,
                    "rank_emoji": rank.emoji,
                    "rank_updated_at": now.isoformat(),
                })
                updated += 1
            except Exception as e:
                logger.warning(f"Rank recompute failed for user {uid}: {e}")

        return updated

    # -- internals ---------------------------------------------------------

    async def _safe(self, fn, *args):
        try:
            return await fn(*args)
        except Exception as e:
            logger.warning(f"Rank score data fetch failed ({getattr(fn, '__name__', fn)}): {e}")
            return None

    async def _fetch_users(self) -> list[dict[str, Any]]:
        def run() -> list[dict[str, Any]]:
            res = (
                self.db._client()
                .table("users")
                .select("id, created_at, trust_score, total_xp, engagement_level, manual_rank_id, reading_streak")
                .execute()
            )
            return res.data or []

        return await asyncio.to_thread(run)

    async def _count_rows(self, table: str, column: str) -> dict[str, int]:
        def run() -> dict[str, int]:
            res = self.db._client().table(table).select(column).execute()
            counts: dict[str, int] = {}
            for row in res.data or []:
                uid = row.get(column)
                if uid:
                    counts[uid] = counts.get(uid, 0) + 1
            return counts

        return await asyncio.to_thread(run)

    async def _quiz_counts(self) -> dict[str, tuple[int, int]]:
        def run() -> dict[str, tuple[int, int]]:
            res = self.db._client().table("lusy_game_history").select("user_id, is_correct").execute()
            out: dict[str, tuple[int, int]] = {}
            for row in res.data or []:
                uid = row.get("user_id")
                if not uid:
                    continue
                played, correct = out.get(uid, (0, 0))
                out[uid] = (played + 1, correct + (1 if row.get("is_correct") else 0))
            return out

        return await asyncio.to_thread(run)

    async def _event_counts(self) -> dict[str, tuple[int, int]]:
        def run() -> dict[str, tuple[int, int]]:
            res = self.db._client().table("event_participants").select("user_id, status, attended_at").execute()
            out: dict[str, tuple[int, int]] = {}
            for row in res.data or []:
                uid = row.get("user_id")
                if not uid:
                    continue
                rsvps, attended = out.get(uid, (0, 0))
                is_attended = row.get("status") == "attended" or bool(row.get("attended_at"))
                out[uid] = (rsvps + 1, attended + (1 if is_attended else 0))
            return out

        return await asyncio.to_thread(run)

    async def _theo_subscribers(self) -> set[str]:
        def run() -> set[str]:
            res = (
                self.db._client()
                .table("user_subscriptions")
                .select("user_id")
                .eq("bot_name", "theo")
                .eq("subscription_type", "daily_devotional")
                .eq("enabled", True)
                .execute()
            )
            return {r["user_id"] for r in (res.data or []) if r.get("user_id")}

        return await asyncio.to_thread(run)

    async def _orientation_completed(self) -> set[str]:
        def run() -> set[str]:
            res = (
                self.db._client()
                .table("moderation_actions")
                .select("user_id")
                .eq("action_type", "orientation_completed")
                .execute()
            )
            return {r["user_id"] for r in (res.data or []) if r.get("user_id")}

        return await asyncio.to_thread(run)
