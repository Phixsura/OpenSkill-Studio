"""Tests for Consumer API Capacity Planner service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_capacity_planner import (
    CapacityPlanner, ResourceMetric,
)


class TestCapacityPlanner:
    def test_set_and_utilization(self):
        svc = CapacityPlanner()
        svc.set_resource(ResourceMetric("cpu", 60, 100, "%"))
        result = svc.get_utilization("cpu")
        assert result["utilization_pct"] == 60.0
        assert result["status"] == "healthy"

    def test_warning_status(self):
        svc = CapacityPlanner()
        svc.set_resource(ResourceMetric("memory", 80, 100, "GB"))
        assert svc.get_utilization("memory")["status"] == "warning"

    def test_critical_status(self):
        svc = CapacityPlanner()
        svc.set_resource(ResourceMetric("storage", 95, 100, "TB"))
        assert svc.get_utilization("storage")["status"] == "critical"

    def test_forecast(self):
        svc = CapacityPlanner()
        svc.set_resource(ResourceMetric("cpu", 50, 100))
        result = svc.forecast("cpu", growth_rate_pct=20, periods=6)
        assert len(result["projections"]) == 6
        assert result["projections"][0]["projected_usage"] == 60.0

    def test_forecast_exhaustion(self):
        svc = CapacityPlanner()
        svc.set_resource(ResourceMetric("cpu", 80, 100))
        result = svc.forecast("cpu", growth_rate_pct=20, periods=6)
        assert result["periods_to_exhaustion"] is not None
        assert result["action_needed"] is True

    def test_forecast_no_exhaustion(self):
        svc = CapacityPlanner()
        svc.set_resource(ResourceMetric("cpu", 10, 100))
        result = svc.forecast("cpu", growth_rate_pct=5, periods=6)
        assert result["periods_to_exhaustion"] is None

    def test_recommend_scaling(self):
        svc = CapacityPlanner()
        svc.set_resource(ResourceMetric("cpu", 85, 100))
        svc.set_resource(ResourceMetric("memory", 30, 100))
        recs = svc.recommend_scaling(target_utilization_pct=70)
        assert len(recs) == 1
        assert recs[0]["resource"] == "cpu"
        assert recs[0]["scale_factor"] > 1

    def test_overview(self):
        svc = CapacityPlanner()
        svc.set_resource(ResourceMetric("cpu", 50, 100))
        svc.set_resource(ResourceMetric("memory", 95, 100))
        overview = svc.get_overview()
        assert overview["total_resources"] == 2
        assert overview["critical"] == 1
        assert overview["healthy"] == 1

    def test_invalid_capacity(self):
        svc = CapacityPlanner()
        with pytest.raises(ValueError):
            svc.set_resource(ResourceMetric("cpu", 50, 0))

    def test_not_found(self):
        svc = CapacityPlanner()
        assert svc.get_utilization("missing")["error"] == "not_found"

    def test_isolation(self):
        a, b = CapacityPlanner(), CapacityPlanner()
        a.set_resource(ResourceMetric("cpu", 50, 100))
        assert b.get_overview()["total_resources"] == 0
