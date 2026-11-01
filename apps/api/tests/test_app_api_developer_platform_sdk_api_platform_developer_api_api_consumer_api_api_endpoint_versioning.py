import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_versioning import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointVersioning

class TestEndpointVersioning:
    def test_register_and_resolve(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointVersioning()
        svc.register("inst-1", "/users", "GET", "v1")
        svc.register("inst-1", "/users", "GET", "v2")
        v = svc.resolve("inst-1", "/users", "GET", "v2")
        assert v is not None and v.version == "v2"

    def test_default_version(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointVersioning()
        svc.register("inst-1", "/api", "GET", "v1")
        v = svc.resolve("inst-1", "/api", "GET")
        assert v.version == "v1"

    def test_sunset_not_resolved(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointVersioning()
        svc.register("inst-1", "/api", "GET", "v1")
        ve = svc._endpoints[("inst-1", "GET", "/api")]
        ve.versions[0].status = "sunset"
        assert svc.resolve("inst-1", "/api", "GET", "v1") is None

    def test_duplicate_version(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointVersioning()
        svc.register("inst-1", "/api", "GET", "v1")
        with pytest.raises(ValueError, match="already registered"):
            svc.register("inst-1", "/api", "GET", "v1")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointVersioning()
        svc.register("inst-1", "/api", "GET", "v1")
        assert len(svc.list_endpoints("inst-2")) == 0
