import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_custom_domain_manager import AppAPIDeveloperPlatformSDKApiDeveloperApiCustomDomainManager

class TestCustomDomainManager:
    def test_add(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiCustomDomainManager()
        d = m.add("inst-1", "api.example.com", "verify-abc123")
        assert d.status == "pending"

    def test_invalid_domain(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiCustomDomainManager()
        with pytest.raises(ValueError):
            m.add("inst-1", "not a domain!", "token")

    def test_cross_tenant_unique(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiCustomDomainManager()
        m.add("inst-1", "api.example.com", "t1")
        with pytest.raises(ValueError, match="already registered"):
            m.add("inst-2", "api.example.com", "t2")

    def test_lifecycle(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiCustomDomainManager()
        m.add("inst-1", "api.example.com", "token")
        m.verify("inst-1", "api.example.com")
        d = m.activate("inst-1", "api.example.com")
        assert d.status == "active"
        assert d.ssl_status == "provisioned"

    def test_activate_requires_verification(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiCustomDomainManager()
        m.add("inst-1", "api.example.com", "token")
        with pytest.raises(ValueError, match="verified"):
            m.activate("inst-1", "api.example.com")

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiCustomDomainManager()
        m.add("inst-1", "api.example.com", "token")
        assert len(m.all_domains("inst-2")) == 0
