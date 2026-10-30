import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_endpoint_permission import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermission, EndpointPermission,
)

class TestConsumerApiEndpointPermission:
    def test_explicit_allow(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermission(default_allowed=False)
        svc.set_permission("inst-1", EndpointPermission(permission_id="p1", consumer_id="c1", endpoint_path="/api/users", method="GET", allowed=True))
        result = svc.check("inst-1", "c1", "/api/users", "GET")
        assert result.allowed and result.reason == "explicit"

    def test_explicit_deny(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermission()
        svc.set_permission("inst-1", EndpointPermission(permission_id="p1", consumer_id="c1", endpoint_path="/api/admin", method="*", allowed=False))
        result = svc.check("inst-1", "c1", "/api/admin", "POST")
        assert not result.allowed

    def test_wildcard_method(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermission()
        svc.set_permission("inst-1", EndpointPermission(permission_id="p1", consumer_id="c1", endpoint_path="/api", method="*", allowed=True, rate_limit_override=100))
        result = svc.check("inst-1", "c1", "/api", "DELETE")
        assert result.allowed and result.rate_limit == 100

    def test_default_allow(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermission(default_allowed=True)
        result = svc.check("inst-1", "c1", "/api/anything", "GET")
        assert result.allowed and result.reason == "default_allow"

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermission()
        svc.set_permission("inst-1", EndpointPermission(permission_id="p1", consumer_id="c1", endpoint_path="/api", method="GET"))
        svc.revoke("inst-1", "c1", "/api", "GET")
        assert len(svc.list_permissions("inst-1", "c1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermission(default_allowed=False)
        svc.set_permission("inst-1", EndpointPermission(permission_id="p1", consumer_id="c1", endpoint_path="/api", method="GET", allowed=True))
        result = svc.check("inst-2", "c1", "/api", "GET")
        assert not result.allowed
