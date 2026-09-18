"""Market insights tests — pure logic, no DB needed."""

from app.talent.services.market_insights import MarketInsightsService

svc = MarketInsightsService()


class TestMarketValue:
    def test_high_demand_low_supply(self):
        mv = svc.compute_market_value(50, 5, "rising")
        assert mv.demand_index > 80
        assert mv.scarcity_index > 80
        assert mv.market_value_score > 80

    def test_low_demand_high_supply(self):
        mv = svc.compute_market_value(2, 50, "declining")
        assert mv.demand_index < 30
        assert mv.scarcity_index == 0  # supply >> demand

    def test_balanced(self):
        mv = svc.compute_market_value(10, 10, "stable")
        assert 30 < mv.market_value_score < 70

    def test_zero_demand(self):
        mv = svc.compute_market_value(0, 10, "declining")
        assert mv.demand_index == 0


class TestCompensationBenchmark:
    def test_suppressed_below_cohort(self):
        b = svc.compute_compensation_benchmark("job", "AI", ["$50k"] * 5)
        assert b.suppressed is True
        assert b.median_display is None

    def test_shows_above_cohort(self):
        vals = [f"${i}k" for i in range(10, 30)]
        b = svc.compute_compensation_benchmark("job", "AI", vals)
        assert b.suppressed is False
        assert b.sample_size == 20
        assert b.min_display is not None
        assert b.max_display is not None


class TestEmployerReputation:
    def test_good_employer(self):
        r = svc.compute_employer_reputation(
            org_id="o1",
            total_placements=20,
            verified_placements=18,
            avg_duration_days=180,
            return_candidates=15,
            total_feedback=20,
            avg_response_hours=4,
        )
        assert r.reputation_score > 70
        assert r.verification_rate > 0.8

    def test_new_employer(self):
        r = svc.compute_employer_reputation(
            org_id="o2",
            total_placements=1,
            verified_placements=0,
            avg_duration_days=None,
            return_candidates=0,
            total_feedback=0,
            avg_response_hours=None,
        )
        assert r.reputation_score < 30

    def test_verification_rate(self):
        r = svc.compute_employer_reputation(
            org_id="o3",
            total_placements=10,
            verified_placements=5,
            avg_duration_days=90,
            return_candidates=3,
            total_feedback=10,
            avg_response_hours=24,
        )
        assert r.verification_rate == 0.5


class TestSkillROI:
    def test_high_roi(self):
        roi = svc.compute_skill_roi(
            capability_id="c1",
            capability_name="AI Design",
            current_opportunities=10,
            opportunities_with_skill=25,
            avg_learning_weeks=8,
        )
        assert roi.roi_rating == "high"
        assert roi.opportunity_unlock_count == 15

    def test_low_roi(self):
        roi = svc.compute_skill_roi(
            capability_id="c2",
            capability_name="Basic Typing",
            current_opportunities=50,
            opportunities_with_skill=52,
            avg_learning_weeks=1,
        )
        assert roi.roi_rating == "low"
