import pytest
from app.services.app_api_endpoint_rate_limit import AppAPIEndpointRateLimit

class TestEndpointRL:
    def test_set(self):
        r = AppAPIEndpointRateLimit()
        rl = r.set_limit("inst-1", "GET", "/api/users", 100)
        assert rl.max_rpm == 100

    def test_allowed(self):
        r = AppAPIEndpointRateLimit()
        r.set_limit("inst-1", "GET", "/api", 5)
        result = r.check("inst-1", "GET", "/api")
        assert result["allowed"] is True

    def test_throttled(self):
        r = AppAPIEndpointRateLimit()
        r.set_limit("inst-1", "GET", "/api", 2)
        r.check("inst-1", "GET", "/api")
        r.check("inst-1", "GET", "/api")
        result = r.check("inst-1", "GET", "/api")
        assert result["allowed"] is False

    def test_no_limit(self):
        r = AppAPIEndpointRateLimit()
        result = r.check("inst-1", "GET", "/unlimited")
        assert result["allowed"] is True

    def test_isolation(self):
        r = AppAPIEndpointRateLimit()
        r.set_limit("inst-1", "GET", "/api", 10)
        assert r.list_limits("inst-2") == []
