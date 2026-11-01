import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_key_scope import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiKeyScope

class TestApiKeyScope:
    def test_create_and_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiKeyScope()
        svc.create_key("inst-1", "k1", ["read", "write"])
        assert svc.check_scope("inst-1", "k1", "read") is True
        assert svc.check_scope("inst-1", "k1", "delete") is False

    def test_admin_grants_all(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiKeyScope()
        svc.create_key("inst-1", "k1", ["admin"])
        assert svc.check_scope("inst-1", "k1", "write") is True
        assert svc.check_scope("inst-1", "k1", "delete") is True

    def test_read_only_rejects_write(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiKeyScope()
        with pytest.raises(ValueError, match="write scopes"):
            svc.create_key("inst-1", "k1", ["read", "write"], read_only=True)

    def test_add_and_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiKeyScope()
        svc.create_key("inst-1", "k1", ["read"])
        svc.add_scope("inst-1", "k1", "write")
        assert svc.check_scope("inst-1", "k1", "write") is True
        svc.revoke_scope("inst-1", "k1", "write")
        assert svc.check_scope("inst-1", "k1", "write") is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiKeyScope()
        svc.create_key("inst-1", "k1", ["read"])
        assert svc.check_scope("inst-2", "k1", "read") is False
        assert len(svc.list_keys("inst-2")) == 0
