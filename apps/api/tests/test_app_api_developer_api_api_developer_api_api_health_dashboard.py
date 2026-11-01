import pytest
from app.services.app_api_developer_api_api_developer_api_api_health_dashboard import AppAPIDeveloperAPIApiDeveloperApiApiHealthDashboard

class TestHealthDashboard:
    def test_register(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiHealthDashboard()
        s = d.register_service("inst-1", "api-gateway")
        assert s.status == "healthy"

    def test_update(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiHealthDashboard()
        d.register_service("inst-1", "api")
        s = d.update_health("inst-1", "api", "degraded", 500, "High latency")
        assert s.consecutive_failures == 1

    def test_overall_healthy(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiHealthDashboard()
        d.register_service("inst-1", "api")
        d.register_service("inst-1", "db")
        assert d.overall_status("inst-1") == "healthy"

    def test_overall_unhealthy(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiHealthDashboard()
        d.register_service("inst-1", "api")
        d.update_health("inst-1", "api", "unhealthy", error_message="Down")
        assert d.overall_status("inst-1") == "unhealthy"

    def test_consecutive_resets(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiHealthDashboard()
        d.register_service("inst-1", "api")
        d.update_health("inst-1", "api", "unhealthy")
        d.update_health("inst-1", "api", "unhealthy")
        d.update_health("inst-1", "api", "healthy")
        assert d.all_services("inst-1")[0].consecutive_failures == 0

    def test_isolation(self):
        d = AppAPIDeveloperAPIApiDeveloperApiApiHealthDashboard()
        d.register_service("inst-1", "api")
        assert len(d.all_services("inst-2")) == 0
