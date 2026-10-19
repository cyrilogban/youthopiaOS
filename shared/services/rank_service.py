from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RankDefinition:
    id: str
    title: str
    tier: str
    min_score: int
    bg_color: str
    text_color: str
    emoji: str
    description: str
    requires_manual_approval: bool = False


RANKS: list[RankDefinition] = [
    # Tier 1: Entry Level (100% Automated)
    RankDefinition("seeker", "YouTopian Seeker", "Entry Level", 0, "#D98A95", "#FFFFFF", "🌸", "A new soul exploring the community.", requires_manual_approval=False),
    RankDefinition("gathered_one", "YouTopian Gathered One", "Entry Level", 101, "#D2B48C", "#1E1B4B", "🌾", "A verified member welcomed into the fold.", requires_manual_approval=False),

    # Tier 2: Active Contributors (100% Automated)
    RankDefinition("spark", "YouTopian Spark", "Active Contributors", 251, "#88C9E8", "#0F172A", "⚡", "Active participant showing initial dedication.", requires_manual_approval=False),
    RankDefinition("luminary", "YouTopian Luminary", "Active Contributors", 501, "#85D6A5", "#0F172A", "💡", "A shining light, active in Scripture quizzes & daily study.", requires_manual_approval=False),
    RankDefinition("witness", "YouTopian Witness", "Active Contributors", 801, "#B8CB80", "#0F172A", "📜", "A seasoned scripture master who exemplifies faith in action.", requires_manual_approval=False),

    # Tier 3: Mentors & Builders (Automated Progression Cap)
    RankDefinition("refiner", "YouTopian Refiner", "Mentors & Builders", 1201, "#B0A8E8", "#1E1B4B", "🔨", "Mentoring newer members and refining the community.", requires_manual_approval=False),
    RankDefinition("pillar", "YouTopian Pillar", "Mentors & Builders", 1701, "#D4628E", "#FFFFFF", "🏛️", "A foundational rock anchoring community discussions.", requires_manual_approval=False),

    # Tier 4: Core Leadership (Strictly Founder Appointed)
    RankDefinition("elite", "YouTopian Elite", "Core Leadership", 2301, "#8EA5D0", "#0F172A", "👑", "Core community leadership, moderators, and coordinators.", requires_manual_approval=True),
    RankDefinition("ambassador", "YouTopian Ambassador", "Core Leadership", 3001, "#B88B97", "#FFFFFF", "🌍", "Global visionary and community director.", requires_manual_approval=True),
]


class RankService:
    """Centralized rank service resolving ranks across the 5-bot ecosystem and Mini App.

    Ranks are resolved from the holistic cross-bot ``rank_score`` (see
    ``shared.services.rank_score_service``), not raw XP, and capped at the
    Pillar ceiling. Elite & Ambassador require founder appointment via
    ``manual_rank_id``.
    """

    MAX_AUTOMATED_RANK_ID: str = "pillar"
    NOMINATION_MIN_SCORE: int = 1701
    NOMINATION_MIN_TRUST: int = 95

    @staticmethod
    def get_all_ranks() -> list[RankDefinition]:
        return RANKS

    @staticmethod
    def get_rank_by_id(rank_id: str) -> RankDefinition | None:
        clean_id = rank_id.lower().strip()
        for rank in RANKS:
            if rank.id == clean_id:
                return rank
        return None

    @classmethod
    def resolve_rank(cls, rank_score: int = 0, manual_rank_id: str | None = None) -> RankDefinition:
        """Resolves the user's official rank.
        - If manual_rank_id is present, uses the manual appointment.
        - Otherwise, resolves rank up to the Pillar ceiling (Tier 3). Elite & Ambassador require manual appointment.
        """
        if manual_rank_id:
            custom = cls.get_rank_by_id(manual_rank_id)
            if custom:
                return custom

        # Automatic score ladder resolution capped at MAX_AUTOMATED_RANK_ID
        current_rank = RANKS[0]
        for rank in RANKS:
            if rank.requires_manual_approval:
                break
            if rank_score >= rank.min_score:
                current_rank = rank
            else:
                break
        return current_rank

    @classmethod
    def resolve_for_user(cls, user: dict[str, Any] | None) -> RankDefinition:
        """Convenience resolver for a Supabase user row (uses stored rank_score)."""
        data = user or {}
        score = int(data.get("rank_score") or 0)
        return cls.resolve_rank(score, data.get("manual_rank_id"))

    @classmethod
    def is_nomination_eligible(cls, rank_score: int = 0, trust_score: int = 100) -> bool:
        """Checks if a member has met the criteria for Founder nomination to Tier 4 (Elite/Ambassador)."""
        return rank_score >= cls.NOMINATION_MIN_SCORE and trust_score >= cls.NOMINATION_MIN_TRUST
