import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_sso_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSsoConfig, SsoConfig,
)

class TestConsumerSsoConfig:
    def test_configure(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSsoConfig()
        cfg = svc.configure("inst-1", SsoConfig(config_id="s1", consumer_id="c1", provider="oidc", domains=["example.com"], enabled=True))
        assert cfg.provider == "oidc"

    def test_domain_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSsoConfig()
        svc.configure("inst-1", SsoConfig(config_id="s1", consumer_id="c1", provider="saml", domains=["corp.com"], enabled=True))
        assert svc.check_domain("inst-1", "user@corp.com") is not None
        assert svc.check_domain("inst-1", "user@other.com") is None

    def test_enforce_requires_enabled(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSsoConfig()
        with pytest.raises(ValueError, match="Cannot enforce disabled"):
            svc.configure("inst-1", SsoConfig(config_id="s1", consumer_id="c1", provider="oidc", enforce=True, enabled=False))

    def test_cannot_disable_enforced(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSsoConfig()
        svc.configure("inst-1", SsoConfig(config_id="s1", consumer_id="c1", provider="oidc", enabled=True, enforce=True))
        with pytest.raises(ValueError, match="Cannot disable enforced"):
            svc.toggle("inst-1", "c1", False)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSsoConfig()
        svc.configure("inst-1", SsoConfig(config_id="s1", consumer_id="c1", provider="saml"))
        assert len(svc.list_configs("inst-2")) == 0
