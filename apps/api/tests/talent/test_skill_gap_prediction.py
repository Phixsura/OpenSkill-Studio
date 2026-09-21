"""Skill gap prediction tests — pure logic, no DB needed."""

from app.talent.services.skill_gap_prediction import SkillGapPredictionService

svc = SkillGapPredictionService()


class TestForecastDemand:
    def test_growing_demand(self):
        d3, d6, d12 = svc.forecast_demand(current_demand=100, growth_rate_90d=0.3)
        assert d3 > 100
        assert d6 > d3
        assert d12 > d6

    def test_declining_demand(self):
        d3, d6, d12 = svc.forecast_demand(current_demand=100, growth_rate_90d=-0.3)
        assert d3 < 100
        assert d12 < d3

    def test_stable_demand(self):
        d3, d6, d12 = svc.forecast_demand(current_demand=100, growth_rate_90d=0.0)
        assert d3 == 100
        assert d12 == 100

    def test_never_negative(self):
        d3, d6, d12 = svc.forecast_demand(current_demand=10, growth_rate_90d=-2.0)
        assert d3 >= 0 and d6 >= 0 and d12 >= 0


class TestForecastSupply:
    def test_supply_growth(self):
        f = svc.forecast_supply(
            capability_id="c1",
            capability_name="AI",
            current_supply=50,
            learners_below_threshold=30,
            avg_months_to_qualify=6,
        )
        assert f.estimated_graduates_3m > 0
        assert f.estimated_graduates_6m > f.estimated_graduates_3m
        assert f.supply_growth_rate > 0

    def test_zero_learners(self):
        f = svc.forecast_supply(
            capability_id="c1",
            capability_name="AI",
            current_supply=50,
            learners_below_threshold=0,
            avg_months_to_qualify=6,
        )
        assert f.estimated_graduates_3m == 0


class TestTimeToClsoure:
    def test_feasible_closure(self):
        e = svc.estimate_time_to_closure(
            capability_id="c1",
            capability_name="AI",
            current_gap=30,
            monthly_supply_growth=5,
            monthly_demand_growth=2,
        )
        assert e.feasible is True
        assert e.estimated_months_to_close == 10.0

    def test_infeasible_gap_growing(self):
        e = svc.estimate_time_to_closure(
            capability_id="c1",
            capability_name="AI",
            current_gap=30,
            monthly_supply_growth=2,
            monthly_demand_growth=5,
        )
        assert e.feasible is False
        assert e.estimated_months_to_close is None


class TestBuildForecast:
    def test_critical_urgency(self):
        f = svc.build_forecast(
            capability_id="c1",
            capability_name="AI Design",
            current_demand=100,
            current_supply=40,
            growth_rate_90d=0.5,
            supply_growth_monthly=1,
        )
        assert f.current_gap == 60
        assert f.predicted_gap_3m > f.current_gap
        assert f.urgency == "critical"

    def test_low_urgency_stable(self):
        f = svc.build_forecast(
            capability_id="c2",
            capability_name="Typing",
            current_demand=10,
            current_supply=50,
            growth_rate_90d=0.0,
            supply_growth_monthly=2,
        )
        assert f.current_gap == 0
        assert f.urgency == "low"

    def test_medium_urgency(self):
        f = svc.build_forecast(
            capability_id="c3",
            capability_name="ML",
            current_demand=50,
            current_supply=30,
            growth_rate_90d=0.1,
            supply_growth_monthly=1,
        )
        assert f.urgency in ("medium", "high")
