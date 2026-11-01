"""Tests for Platform Command Center service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_command_center import (
    CommandCenter, ServiceStatus,
)


class TestCommandCenter:
    def test_register_and_overview(self):
        svc = CommandCenter()
        svc.register_service(ServiceStatus("auth", "operational", 99.99))
        svc.register_service(ServiceStatus("api", "operational", 99.95))
        overview = svc.get_overview()
        assert overview["platform_status"] == "all_operational"
        assert overview["services"]["total"] == 2

    def test_degraded_status(self):
        svc = CommandCenter()
        svc.register_service(ServiceStatus("auth", "operational"))
        svc.register_service(ServiceStatus("search", "degraded"))
        overview = svc.get_overview()
        assert overview["platform_status"] == "partial_outage"

    def test_outage_status(self):
        svc = CommandCenter()
        svc.register_service(ServiceStatus("db", "outage"))
        overview = svc.get_overview()
        assert overview["platform_status"] == "major_outage"

    def test_update_status_triggers_alert(self):
        svc = CommandCenter()
        svc.register_service(ServiceStatus("api", "operational"))
        result = svc.update_status("api", "degraded")
        assert result["changed"] is True
        overview = svc.get_overview()
        assert len(overview["recent_alerts"]) == 1

    def test_update_metrics(self):
        svc = CommandCenter()
        svc.update_metrics(total_consumers=150, total_endpoints=45)
        overview = svc.get_overview()
        assert overview["metrics"]["total_consumers"] == 150

    def test_health_score_perfect(self):
        svc = CommandCenter()
        svc.register_service(ServiceStatus("a", "operational", 100.0))
        svc.register_service(ServiceStatus("b", "operational", 100.0))
        score = svc.get_health_score()
        assert score["grade"] == "A"

    def test_health_score_with_outage(self):
        svc = CommandCenter()
        svc.register_service(ServiceStatus("a", "operational", 100.0))
        svc.register_service(ServiceStatus("b", "outage", 80.0))
        score = svc.get_health_score()
        assert score["grade"] in ("C", "D", "F")

    def test_service_list(self):
        svc = CommandCenter()
        svc.register_service(ServiceStatus("beta", "operational"))
        svc.register_service(ServiceStatus("alpha", "degraded"))
        services = svc.get_service_list()
        assert services[0]["name"] == "alpha"

    def test_add_alert(self):
        svc = CommandCenter()
        svc.add_alert("threshold", "CPU > 90%", "warning")
        overview = svc.get_overview()
        assert len(overview["recent_alerts"]) == 1

    def test_invalid_status(self):
        svc = CommandCenter()
        svc.register_service(ServiceStatus("api", "operational"))
        with pytest.raises(ValueError):
            svc.update_status("api", "broken")

    def test_isolation(self):
        a, b = CommandCenter(), CommandCenter()
        a.register_service(ServiceStatus("api", "operational"))
        assert b.get_service_list() == []
