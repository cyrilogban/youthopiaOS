from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RankDefinition:
    id: str
    title: str
    tier: str
    min_xp: int
    bg_color: str
    text_color: str
    emoji: str
    description: str
    requires_manual_approval: bool = False


RANKS: list[RankDefinition] = [
    # Tier 1: Entry Level (100% Automated)
    RankDefinition("seeker", "YouTopian Seeker", "Entry Level", 0, "#D98A95", "#FFFFFF", "🌸", "A new soul exploring the community.", requires_manual_approval=False),
    RankDefinition("gathered_one", "YouTopian Gathered One", "Entry Level", 50, "#D2B48C", "#1E1B4B", "🌾", "A verified member welcomed into the fold.", requires_manual_approval=False),
    
    # Tier 2: Active Contributors (100% Automated)
    RankDefinition("spark", "YouTopian Spark", "Active Contributors", 100, "#88C9E8", "#0F172A", "⚡", "Active participant showing initial dedication.", requires_manual_approval=False),
    RankDefinition("luminary", "YouTopian Luminary", "Active Contributors", 500, "#85D6A5", "#0F172A", "💡", "A shining light, active in Scripture quizzes & daily study.", requires_manual_approval=False),
    RankDefinition("witness", "YouTopian Witness", "Active Contributors", 1000, "#B8CB80", "#0F172A", "📜", "A seasoned scripture master who exemplifies faith in action.", requires_manual_approval=False),
    
    # Tier 3: Mentors & Builders (Automated Progression Cap)
    RankDefinition("refiner", "YouTopian Refiner", "Mentors & Builders", 2500, "#B0A8E8", "#1E1B4B", "🔨", "Mentoring newer members and refining the community.", requires_manual_approval=False),
    RankDefinition("pillar", "YouTopian Pillar", "Mentors & Builders", 5000, "#D4628E", "#FFFFFF", "🏛️", "A foundational rock anchoring community discussions.", requires_manual_approval=False),
    
    # Tier 4: Core Leadership (Strictly Founder Appointed)
    RankDefinition("elite", "YouTopian Elite", "Core Leadership", 10000, "#8EA5D0", "#0F172A", "👑", "Core community leadership, moderators, and coordinators.", requires_manual_approval=True),
    RankDefinition("ambassador", "YouTopian Ambassador", "Core Leadership", 25000, "#B88B97", "#FFFFFF", "🌍", "Global visionary and community director.", requires_manual_approval=True),
]


class RankService:
    """Centralized rank service resolving ranks across the 5-bot ecosystem and Mini App."""

    MAX_AUTOMATED_RANK_ID: str = "pillar"
    NOMINATION_MIN_XP: int = 10000
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
    def resolve_rank(cls, total_xp: int = 0, manual_rank_id: str | None = None) -> RankDefinition:
        """Resolves the user's official rank.
        - If manual_rank_id is present, uses the manual appointment.
        - Otherwise, resolves rank up to the Pillar ceiling (Tier 3). Elite & Ambassador require manual appointment.
        """
        if manual_rank_id:
            custom = cls.get_rank_by_id(manual_rank_id)
            if custom:
                return custom

        # Automatic XP Ladder resolution capped at MAX_AUTOMATED_RANK_ID
        current_rank = RANKS[0]
        for rank in RANKS:
            if rank.requires_manual_approval:
                break
            if total_xp >= rank.min_xp:
                current_rank = rank
            else:
                break
        return current_rank

    @classmethod
    def is_nomination_eligible(cls, total_xp: int = 0, trust_score: int = 100) -> bool:
        """Checks if a member has met the criteria for Founder nomination to Tier 4 (Elite/Ambassador)."""
        return total_xp >= cls.NOMINATION_MIN_XP and trust_score >= cls.NOMINATION_MIN_TRUST
