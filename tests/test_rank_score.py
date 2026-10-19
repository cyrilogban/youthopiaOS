from shared.services.rank_score_service import RankScoreInputs, compute_rank_score
from shared.services.rank_service import RankService


def test_new_member_defaults_to_seeker():
    score = compute_rank_score(RankScoreInputs())
    assert score == 100
    assert RankService.resolve_rank(score).id == "seeker"


def test_onboarded_member_reaches_gathered_one():
    score = compute_rank_score(RankScoreInputs(onboarded=True))
    assert score == 200
    assert RankService.resolve_rank(score).id == "gathered_one"


def test_components_are_capped_independently():
    score = compute_rank_score(RankScoreInputs(
        total_xp=100_000,
        quizzes_played=10_000,
        correct_answers=10_000,
        saved_verses=10_000,
        reading_streak=10_000,
        votd_subscribed=True,
        rsvps=10_000,
        events_attended=10_000,
        onboarded=True,
        days_in_community=100_000,
    ))
    # theo 150 + 25 + 100 | lusie 400 + 100 + 150 | pete 100 | edie 150 + 250 | susie 100 | time 500
    assert score == 275 + 650 + 100 + 400 + 100 + 500


def test_accurately_penalizes_low_accuracy():
    perfect = compute_rank_score(RankScoreInputs(quizzes_played=10, correct_answers=10))
    zero = compute_rank_score(RankScoreInputs(quizzes_played=10, correct_answers=0))
    assert perfect - zero == 150


def test_auto_ladder_is_capped_at_pillar():
    assert RankService.resolve_rank(500).id == "spark"
    assert RankService.resolve_rank(801).id == "witness"
    assert RankService.resolve_rank(1701).id == "pillar"
    # Even a huge auto score never reaches founder-appointed ranks.
    assert RankService.resolve_rank(999_999).id == "pillar"


def test_manual_rank_override_wins():
    assert RankService.resolve_rank(0, "elite").id == "elite"
    assert RankService.resolve_for_user({"rank_score": 0, "manual_rank_id": "ambassador"}).id == "ambassador"


def test_resolve_for_user_uses_rank_score():
    user = {"rank_score": 900, "manual_rank_id": None}
    assert RankService.resolve_for_user(user).id == "witness"
    assert RankService.resolve_for_user({}).id == "seeker"


def test_nomination_eligibility_is_score_based():
    assert RankService.is_nomination_eligible(1701, 95) is True
    assert RankService.is_nomination_eligible(1700, 95) is False
    assert RankService.is_nomination_eligible(5000, 94) is False
