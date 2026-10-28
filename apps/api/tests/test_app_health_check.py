"""Tests for App Health Check — register, record, uptime, latency."""

import pytest

from app.services.app_health_check import AppHealthCheck, HealthStatus


class TestRegister:
    def test_register(self):
        h = AppHealthCheck()
        ep = h.register("inst-1", "api", "https://api.example.com/health")
        assert ep.url == "https://api.example.com/health"
        assert ep.current_status is None

    def test_missing_url(self):
        h = AppHealthCheck()
        with pytest.raises(ValueError):
            h.register("inst-1", "api", "")


class TestRecord:
    def test_record_up(self):
        h = AppHealthCheck()
        h.register("inst-1", "api", "https://api/health")
        r = h.record("inst-1", "api", HealthStatus.UP, 45.2)
        assert r.status == HealthStatus.UP

    def test_status_updates(self):
        h = AppHealthCheck()
        h.register("inst-1", "api", "https://api/health")
        h.record("inst-1", "api", HealthStatus.UP, 50)
        h.record("inst-1", "api", HealthStatus.DOWN, 0, "Connection refused")
        assert h.get_status("inst-1", "api") == HealthStatus.DOWN


class TestUptime:
    def test_uptime(self):
        h = AppHealthCheck()
        h.register("inst-1", "api", "https://api/health")
        for _ in range(8):
            h.record("inst-1", "api", HealthStatus.UP, 50)
        for _ in range(2):
            h.record("inst-1", "api", HealthStatus.DOWN, 0)
        assert h.get_uptime("inst-1", "api") == 80.0

    def test_no_results(self):
        h = AppHealthCheck()
        h.register("inst-1", "api", "https://api/health")
        assert h.get_uptime("inst-1", "api") == 100.0


class TestLatency:
    def test_avg(self):
        h = AppHealthCheck()
        h.register("inst-1", "api", "https://api/health")
        h.record("inst-1", "api", HealthStatus.UP, 100)
        h.record("inst-1", "api", HealthStatus.UP, 200)
        assert h.avg_latency("inst-1", "api") == 150.0


class TestDown:
    def test_down_endpoints(self):
        h = AppHealthCheck()
        h.register("inst-1", "api", "https://api/health")
        h.register("inst-1", "db", "https://db/health")
        h.record("inst-1", "api", HealthStatus.UP, 50)
        h.record("inst-1", "db", HealthStatus.DOWN, 0)
        down = h.down_endpoints("inst-1")
        assert len(down) == 1
        assert down[0].endpoint_id == "db"


class TestIsolation:
    def test_cross(self):
        h = AppHealthCheck()
        h.register("inst-1", "api", "https://api/health")
        assert h.list_endpoints("inst-2") == []
