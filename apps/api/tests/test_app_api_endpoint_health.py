"""Tests for App API Endpoint Health — record, degraded, top errors."""

from app.services.app_api_endpoint_health import AppAPIEndpointHealth


class TestRecord:
    def test_record(self):
        h = AppAPIEndpointHealth()
        ep = h.record("inst-1", "GET", "/api/users", True)
        assert ep.total == 1
        assert ep.error_rate == 0.0


class TestDegraded:
    def test_degraded(self):
        h = AppAPIEndpointHealth()
        for _ in range(9):
            h.record("inst-1", "GET", "/api/bad", True)
        for _ in range(3):
            h.record("inst-1", "GET", "/api/bad", False)
        assert len(h.degraded_endpoints("inst-1")) == 1

    def test_healthy(self):
        h = AppAPIEndpointHealth()
        for _ in range(100):
            h.record("inst-1", "GET", "/api/good", True)
        h.record("inst-1", "GET", "/api/good", False)
        assert h.degraded_endpoints("inst-1") == []


class TestTopErrors:
    def test_ranked(self):
        h = AppAPIEndpointHealth()
        for _ in range(5):
            h.record("inst-1", "GET", "/api/a", False)
        for _ in range(2):
            h.record("inst-1", "POST", "/api/b", False)
        top = h.top_errors("inst-1")
        assert top[0].path == "/api/a"


class TestIsolation:
    def test_cross(self):
        h = AppAPIEndpointHealth()
        h.record("inst-1", "GET", "/api", True)
        assert h.list_endpoints("inst-2") == []
