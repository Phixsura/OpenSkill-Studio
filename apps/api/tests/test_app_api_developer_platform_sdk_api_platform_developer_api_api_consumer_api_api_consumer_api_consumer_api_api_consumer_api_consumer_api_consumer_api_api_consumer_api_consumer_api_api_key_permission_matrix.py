import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_key_permission_matrix import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrix, PermissionEntry,
)

class TestApiKeyPermissionMatrix:
    def test_explicit_allow(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrix()
        svc.set_permission("inst-1", "c1", PermissionEntry(key_id="k1", endpoint_path="/api/users", method="GET", allowed=True))
        result = svc.check("inst-1", "c1", "k1", "/api/users", "GET")
        assert result.allowed and result.reason == "explicit_allow"

    def test_explicit_deny(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrix()
        svc.set_permission("inst-1", "c1", PermissionEntry(key_id="k1", endpoint_path="/api/admin", method="*", allowed=False))
        result = svc.check("inst-1", "c1", "k1", "/api/admin", "POST")
        assert not result.allowed and result.reason == "explicit_deny"

    def test_default_deny(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrix(default_allow=False)
        result = svc.check("inst-1", "c1", "k1", "/api/anything", "GET")
        assert not result.allowed and result.reason == "default"

    def test_wildcard_method(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrix()
        svc.set_permission("inst-1", "c1", PermissionEntry(key_id="k1", endpoint_path="/api", method="*", allowed=True))
        assert svc.check("inst-1", "c1", "k1", "/api", "DELETE").allowed

    def test_revoke_all(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrix()
        svc.set_permission("inst-1", "c1", PermissionEntry(key_id="k1", endpoint_path="/a", method="GET"))
        svc.set_permission("inst-1", "c1", PermissionEntry(key_id="k1", endpoint_path="/b", method="POST"))
        removed = svc.revoke_all("inst-1", "c1", "k1")
        assert removed == 2 and len(svc.get_matrix("inst-1", "c1", "k1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiKeyPermissionMatrix()
        svc.set_permission("inst-1", "c1", PermissionEntry(key_id="k1", endpoint_path="/api", method="GET", allowed=True))
        assert svc.check("inst-2", "c1", "k1", "/api", "GET").reason == "default"
