import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_sso_provider import AppAPIDeveloperPlatformSDKApiDeveloperApiSSOProvider

class TestSSOProvider:
    def test_configure(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiSSOProvider()
        p = s.configure("inst-1", "p1", "oidc", "https://auth.example.com", "client-123")
        assert p.provider_type == "oidc"

    def test_https_required(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiSSOProvider()
        with pytest.raises(ValueError):
            s.configure("inst-1", "p1", "oidc", "http://bad.com", "client-123")

    def test_login(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiSSOProvider()
        s.configure("inst-1", "p1", "saml", "https://auth.com", "c1")
        p = s.record_login("inst-1", "p1")
        assert p.login_count == 1

    def test_disabled_blocks_login(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiSSOProvider()
        s.configure("inst-1", "p1", "oidc", "https://auth.com", "c1")
        s.toggle("inst-1", "p1", False)
        with pytest.raises(ValueError, match="disabled"):
            s.record_login("inst-1", "p1")

    def test_active_providers(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiSSOProvider()
        s.configure("inst-1", "p1", "oidc", "https://a.com", "c1")
        s.configure("inst-1", "p2", "saml", "https://b.com", "c2")
        s.toggle("inst-1", "p1", False)
        assert len(s.active_providers("inst-1")) == 1

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiDeveloperApiSSOProvider()
        s.configure("inst-1", "p1", "oidc", "https://a.com", "c1")
        assert len(s.all_providers("inst-2")) == 0
