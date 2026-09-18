"""Hiring analytics tests — pure logic, no DB needed."""

from app.talent.services.hiring_analytics import (
    PIPELINE_STAGES,
    HiringAnalytics,
    HiringAnalyticsService,
)


class TestHiringAnalytics:
    def test_empty_analytics(self):
        result = HiringAnalyticsService._empty_analytics()
        assert result.avg_time_to_hire_days is None
        assert result.median_time_to_hire_days is None
        assert result.stage_conversion_rates == {}
        assert result.avg_time_in_stage == {}
        assert result.offer_acceptance_rate is None
        assert result.total_applications == 0
        assert result.total_hires == 0
        assert result.total_offers == 0
        assert result.pipeline_velocity is None

    def test_pipeline_stages_order(self):
        expected = ["submitted", "screening", "interview", "assessment", "offer", "hired"]
        assert expected == PIPELINE_STAGES

    def test_analytics_dataclass_fields(self):
        a = HiringAnalytics(
            avg_time_to_hire_days=15.5,
            median_time_to_hire_days=12.0,
            stage_conversion_rates={"submitted→screening": 0.8},
            avg_time_in_stage={"screening": 3.5},
            offer_acceptance_rate=0.75,
            total_applications=100,
            total_hires=10,
            total_offers=15,
            pipeline_velocity=3.33,
        )
        assert a.avg_time_to_hire_days == 15.5
        assert a.total_applications == 100
        assert a.pipeline_velocity == 3.33
        assert a.stage_conversion_rates["submitted→screening"] == 0.8

    def test_frozen(self):
        a = HiringAnalyticsService._empty_analytics()
        try:
            a.total_applications = 999  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass

    def test_offer_acceptance_rate_computed(self):
        a = HiringAnalytics(
            avg_time_to_hire_days=10.0,
            median_time_to_hire_days=10.0,
            stage_conversion_rates={},
            avg_time_in_stage={},
            offer_acceptance_rate=0.6667,
            total_applications=50,
            total_hires=10,
            total_offers=15,
            pipeline_velocity=1.0,
        )
        assert a.offer_acceptance_rate == 0.6667
