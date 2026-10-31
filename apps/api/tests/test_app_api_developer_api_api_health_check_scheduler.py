import pytest
from app.services.app_api_developer_api_api_health_check_scheduler import AppAPIDeveloperAPIApiHealthCheckScheduler

class TestHealthCheckScheduler:
    def test_schedule(self):
        s = AppAPIDeveloperAPIApiHealthCheckScheduler()
        c = s.schedule("inst-1", "c1", "/health", 30)
        assert c.last_result == "unknown"

    def test_min_interval(self):
        s = AppAPIDeveloperAPIApiHealthCheckScheduler()
        with pytest.raises(ValueError):
            s.schedule("inst-1", "c1", "/health", 5)

    def test_healthy(self):
        s = AppAPIDeveloperAPIApiHealthCheckScheduler()
        s.schedule("inst-1", "c1", "/health", 30)
        c = s.record_result("inst-1", "c1", 200, 50)
        assert c.last_result == "healthy"
        assert c.consecutive_failures == 0

    def test_unhealthy(self):
        s = AppAPIDeveloperAPIApiHealthCheckScheduler()
        s.schedule("inst-1", "c1", "/health", 30)
        s.record_result("inst-1", "c1", 500, 50)
        s.record_result("inst-1", "c1", 500, 50)
        c = s.all_checks("inst-1")[0]
        assert c.consecutive_failures == 2
        assert len(s.unhealthy_checks("inst-1")) == 1

    def test_timeout(self):
        s = AppAPIDeveloperAPIApiHealthCheckScheduler()
        s.schedule("inst-1", "c1", "/health", 30, timeout_ms=100)
        c = s.record_result("inst-1", "c1", 200, 200)
        assert c.last_result == "timeout"

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiHealthCheckScheduler()
        s.schedule("inst-1", "c1", "/health", 30)
        assert len(s.all_checks("inst-2")) == 0
