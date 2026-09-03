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


RANKS: list[RankDefinition] = [
    # Tier 1: Entry Level
    RankDefinition("seeker", "YouTopian Seeker", "Entry Level", 0, "#D98A95", "#FFFFFF", "🌸", "A new soul exploring the community."),
    RankDefinition("gathered_one", "YouTopian Gathered One", "Entry Level", 50, "#D2B48C", "#1E1B4B", "🌾", "A verified member welcomed into the fold."),
    
    # Tier 2: Active Contributors
    RankDefinition("spark", "YouTopian Spark", "Active Contributors", 100, "#88C9E8", "#0F172A", "⚡", "Active participant showing initial dedication."),
    RankDefinition("luminary", "YouTopian Luminary", "Active Contributors", 500, "#85D6A5", "#0F172A", "💡", "A shining light, active in Scripture quizzes & daily study."),
    RankDefinition("witness", "YouTopian Witness", "Active Contributors", 1000, "#B8CB80", "#0F172A", "📜", "A seasoned scripture master who exemplifies faith in action."),
    
    # Tier 3: Mentors & Builders
    RankDefinition("refiner", "YouTopian Refiner", "Mentors & Builders", 2500, "#B0A8E8", "#1E1B4B", "🔨", "Mentoring newer members and refining the community."),
    RankDefinition("pillar", "YouTopian Pillar", "Mentors & Builders", 5000, "#D4628E", "#FFFFFF", "🏛️", "A foundational rock anchoring community discussions."),
    
    # Tier 4: Core Leadership
    RankDefinition("elite", "YouTopian Elite", "Core Leadership", 10000, "#8EA5D0", "#0F172A", "👑", "Core community leadership, moderators, and coordinators."),
    RankDefinition("ambassador", "YouTopian Ambassador", "Core Leadership", 25000, "#B88B97", "#FFFFFF", "🌍", "Global visionary and community director."),
]


class RankService:
    """Centralized rank service resolving ranks across the 5-bot ecosystem and Mini App."""

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

    @staticmethod
    def resolve_rank(total_xp: int = 0, manual_rank_id: str | None = None) -> RankDefinition:
        """Resolves the user's official rank based on manual appointment or automatic XP ladder."""
        if manual_rank_id:
            custom = RankService.get_rank_by_id(manual_rank_id)
            if custom:
                return custom

        # Automatic XP Ladder resolution
        current_rank = RANKS[0]
        for rank in RANKS:
            if total_xp >= rank.min_xp:
                current_rank = rank
            else:
                break
        return current_rank
