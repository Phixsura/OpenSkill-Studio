"""Tests for App API Endpoint Version — register, query, deprecated."""

from app.services.app_api_endpoint_version import AppAPIEndpointVersion


class TestRegister:
    def test_register(self):
        v = AppAPIEndpointVersion()
        ep = v.register("inst-1", "GET", "/api/users", "v2")
        assert ep.version == "v2"


class TestQuery:
    def test_for_version(self):
        v = AppAPIEndpointVersion()
        v.register("inst-1", "GET", "/api/users", "v1")
        v.register("inst-1", "GET", "/api/users", "v2")
        v.register("inst-1", "POST", "/api/apps", "v2")
        assert len(v.endpoints_for_version("inst-1", "v2")) == 2

    def test_versions_for_endpoint(self):
        v = AppAPIEndpointVersion()
        v.register("inst-1", "GET", "/api/users", "v1")
        v.register("inst-1", "GET", "/api/users", "v2")
        assert v.versions_for_endpoint("inst-1", "GET", "/api/users") == ["v1", "v2"]

    def test_deprecated(self):
        v = AppAPIEndpointVersion()
        v.register("inst-1", "GET", "/api/old", "v1", deprecated=True)
        v.register("inst-1", "GET", "/api/new", "v2")
        assert len(v.deprecated_endpoints("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        v = AppAPIEndpointVersion()
        v.register("inst-1", "GET", "/api", "v1")
        assert v.list_all("inst-2") == []
