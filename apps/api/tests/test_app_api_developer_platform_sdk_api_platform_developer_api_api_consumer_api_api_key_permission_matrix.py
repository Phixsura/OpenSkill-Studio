from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_key_permission_matrix import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyPermissionMatrix, KeyPermissionMatrix, PermissionEntry,
)

class TestKeyPermissionMatrix:
    def test_allowed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyPermissionMatrix()
        svc.set_matrix("inst-1", KeyPermissionMatrix(key_id="k1", consumer_id="c1", permissions=[PermissionEntry("/users", "GET", True)]))
        assert svc.check_permission("inst-1", "k1", "GET", "/users") is True

    def test_denied(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyPermissionMatrix()
        svc.set_matrix("inst-1", KeyPermissionMatrix(key_id="k1", consumer_id="c1", permissions=[PermissionEntry("/admin", "DELETE", False)]))
        assert svc.check_permission("inst-1", "k1", "DELETE", "/admin") is False

    def test_fail_closed_unknown_key(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyPermissionMatrix()
        assert svc.check_permission("inst-1", "unknown", "GET", "/any") is False

    def test_fail_closed_unmatched(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyPermissionMatrix()
        svc.set_matrix("inst-1", KeyPermissionMatrix(key_id="k1", consumer_id="c1", default_allow=False))
        assert svc.check_permission("inst-1", "k1", "GET", "/unmatched") is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyPermissionMatrix()
        svc.set_matrix("inst-1", KeyPermissionMatrix(key_id="k1", consumer_id="c1"))
        assert len(svc.list_matrices("inst-2")) == 0
