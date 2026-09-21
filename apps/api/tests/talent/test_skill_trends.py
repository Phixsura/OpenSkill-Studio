"""Skill trending and obsolescence detection tests — pure logic."""

from app.talent.services.skill_trends import (
    TREND_WINDOW_DAYS,
    SkillTrend,
    _classify_trend,
)


class TestClassifyTrend:
    def test_both_zero_is_stable(self):
        direction, growth = _classify_trend(0, 0, 100)
        assert direction == "stable"
        assert growth == 0.0

    def test_rising_trend(self):
        # current=10, prior=5 → growth = (10-5)/5 = 1.0 > 0.2
        direction, growth = _classify_trend(10, 5, 100)
        assert direction == "rising"
        assert growth > 0.2

    def test_cooling_trend(self):
        # current=2, prior=10 → growth = (2-10)/10 = -0.8 < -0.2
        direction, growth = _classify_trend(2, 10, 100)
        assert direction == "cooling"
        assert growth < -0.2

    def test_stable_trend(self):
        # current=10, prior=9 → growth = (10-9)/9 ≈ 0.11 → stable
        direction, growth = _classify_trend(10, 9, 100)
        assert direction == "stable"
        assert -0.2 <= growth <= 0.2

    def test_emerging_skill_small_total(self):
        # total < 10, current > 0 → emerging
        direction, growth = _classify_trend(5, 2, 7)
        assert direction == "emerging"

    def test_emerging_with_zero_prior(self):
        direction, growth = _classify_trend(3, 0, 3)
        assert direction == "emerging"
        assert growth == 3.0  # (3-0)/max(0,1) = 3.0

    def test_large_total_not_emerging(self):
        # total >= 10, so not emerging even if growth is high
        direction, growth = _classify_trend(8, 2, 50)
        assert direction == "rising"  # not emerging

    def test_zero_current_nonzero_prior_is_cooling(self):
        direction, growth = _classify_trend(0, 5, 100)
        assert direction == "cooling"
        assert growth == -1.0  # (0-5)/5 = -1.0

    def test_growth_rate_precision(self):
        _, growth = _classify_trend(15, 10, 100)
        # (15-10)/10 = 0.5
        assert growth == 0.5


class TestSkillTrend:
    def test_dataclass_fields(self):
        trend = SkillTrend(
            capability_id="cap1",
            capability_name="Python",
            category="programming",
            trend_direction="rising",
            current_period_count=10,
            prior_period_count=5,
            growth_rate=1.0,
            demand_count=20,
            supply_count=15,
        )
        assert trend.capability_id == "cap1"
        assert trend.trend_direction == "rising"
        assert trend.growth_rate == 1.0

    def test_frozen(self):
        trend = SkillTrend(
            capability_id="cap1",
            capability_name="Python",
            category="programming",
            trend_direction="rising",
            current_period_count=10,
            prior_period_count=5,
            growth_rate=1.0,
            demand_count=20,
            supply_count=15,
        )
        try:
            trend.growth_rate = 2.0  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass


class TestConstants:
    def test_trend_window_days(self):
        assert TREND_WINDOW_DAYS == 90
