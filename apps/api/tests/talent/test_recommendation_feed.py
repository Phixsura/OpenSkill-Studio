"""Recommendation feed tests — signal weights and scoring logic (N19)."""

from app.talent.services.recommendation_feed import (
    _RECENCY_WINDOW_DAYS,
    _W_CAPABILITY,
    _W_ENGAGEMENT,
    _W_GOAL,
    _W_RECENCY,
    _W_TYPE_PREF,
    RecommendedOpportunity,
)


class TestSignalWeights:
    def test_weights_sum_to_one(self):
        total = _W_CAPABILITY + _W_TYPE_PREF + _W_GOAL + _W_RECENCY + _W_ENGAGEMENT
        assert abs(total - 1.0) < 0.001

    def test_capability_highest_weight(self):
        assert _W_CAPABILITY > _W_TYPE_PREF
        assert _W_CAPABILITY > _W_GOAL
        assert _W_CAPABILITY > _W_RECENCY
        assert _W_CAPABILITY > _W_ENGAGEMENT

    def test_recency_window(self):
        assert _RECENCY_WINDOW_DAYS == 90


class TestRecommendedOpportunity:
    def test_immutable(self):
        rec = RecommendedOpportunity(
            opportunity_id="opp1",
            title="AI Designer",
            opportunity_type="internship",
            employer_org_id="org1",
            match_score=0.85,
            match_reasons=["Strong capability match"],
            is_bookmarked=False,
            already_applied=False,
            closes_in_days=14,
        )
        assert rec.match_score == 0.85
        assert rec.closes_in_days == 14

        try:
            rec.match_score = 0.9  # type: ignore[misc]
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass

    def test_fields_present(self):
        rec = RecommendedOpportunity(
            opportunity_id="opp1",
            title="Test",
            opportunity_type="job",
            employer_org_id="org1",
            match_score=0.5,
            match_reasons=[],
            is_bookmarked=True,
            already_applied=False,
            closes_in_days=None,
        )
        assert rec.is_bookmarked is True
        assert rec.already_applied is False
        assert rec.closes_in_days is None

    def test_multiple_reasons(self):
        rec = RecommendedOpportunity(
            opportunity_id="opp1",
            title="Test",
            opportunity_type="internship",
            employer_org_id="org1",
            match_score=0.9,
            match_reasons=[
                "Strong capability match",
                "Preferred type: internship",
                "Aligns with career goals",
            ],
            is_bookmarked=False,
            already_applied=False,
            closes_in_days=7,
        )
        assert len(rec.match_reasons) == 3


class TestMaxScore:
    def test_max_possible_score(self):
        # All signals at 1.0
        max_score = (
            _W_CAPABILITY * 1.0
            + _W_TYPE_PREF * 1.0
            + _W_GOAL * 1.0
            + _W_RECENCY * 1.0
            + _W_ENGAGEMENT * 1.0
        )
        assert abs(max_score - 1.0) < 0.001

    def test_min_possible_score(self):
        # All signals at 0.0
        min_score = (
            _W_CAPABILITY * 0.0
            + _W_TYPE_PREF * 0.0
            + _W_GOAL * 0.0
            + _W_RECENCY * 0.0
            + _W_ENGAGEMENT * 0.0
        )
        assert min_score == 0.0
