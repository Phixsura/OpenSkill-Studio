import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_versioned_endpoint_router import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouter

class TestVersionedEndpointRouter:
    def test_register_and_route(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouter()
        r.register("inst-1", "/api/users", "v1", "handler_v1")
        r.register("inst-1", "/api/users", "v2", "handler_v2", default=True)
        assert r.route("inst-1", "/api/users") == "handler_v2"
        assert r.route("inst-1", "/api/users", "v1") == "handler_v1"

    def test_unknown_version(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouter()
        r.register("inst-1", "/api/users", "v1", "handler_v1")
        with pytest.raises(KeyError):
            r.route("inst-1", "/api/users", "v99")

    def test_traffic_tracking(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouter()
        r.register("inst-1", "/api", "v1", "h1")
        r.register("inst-1", "/api", "v2", "h2")
        r.route("inst-1", "/api", "v1")
        r.route("inst-1", "/api", "v1")
        r.route("inst-1", "/api", "v2")
        traffic = r.version_traffic("inst-1", "/api")
        assert traffic["v1"] == 2
        assert traffic["v2"] == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouter()
        r.register("inst-1", "/api", "v1", "h1")
        assert len(r.all_routes("inst-2")) == 0
