"""Tests for App API Gateway — routes, resolve, header injection."""

import pytest

from app.services.app_api_gateway import AppAPIGateway


class TestAddRoute:
    def test_add(self):
        g = AppAPIGateway()
        r = g.add_route("inst-1", "r1", "/api/users", "http://users-svc:8080")
        assert r.strip_prefix is True

    def test_invalid_prefix(self):
        g = AppAPIGateway()
        with pytest.raises(ValueError, match="start with /"):
            g.add_route("inst-1", "r1", "api", "http://svc")


class TestResolve:
    def test_resolve_strip(self):
        g = AppAPIGateway()
        g.add_route("inst-1", "r1", "/api/users", "http://users-svc:8080")
        result = g.resolve("inst-1", "/api/users/123")
        assert result is not None
        assert result["upstream"] == "http://users-svc:8080"
        assert result["path"] == "/123"

    def test_resolve_no_strip(self):
        g = AppAPIGateway()
        g.add_route("inst-1", "r1", "/api", "http://backend", strip_prefix=False)
        result = g.resolve("inst-1", "/api/v1/health")
        assert result["path"] == "/api/v1/health"

    def test_no_match(self):
        g = AppAPIGateway()
        g.add_route("inst-1", "r1", "/api", "http://backend")
        assert g.resolve("inst-1", "/other") is None

    def test_disabled(self):
        g = AppAPIGateway()
        g.add_route("inst-1", "r1", "/api", "http://backend")
        g.toggle("inst-1", "r1", False)
        assert g.resolve("inst-1", "/api/test") is None

    def test_inject_headers(self):
        g = AppAPIGateway()
        g.add_route("inst-1", "r1", "/api", "http://backend", inject_headers={"X-Tenant": "acme"})
        result = g.resolve("inst-1", "/api/test")
        assert result["headers"]["X-Tenant"] == "acme"


class TestIsolation:
    def test_cross(self):
        g = AppAPIGateway()
        g.add_route("inst-1", "r1", "/api", "http://backend")
        assert g.resolve("inst-2", "/api") is None
