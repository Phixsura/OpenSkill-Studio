import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_developer_portal_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDeveloperPortalConfig, PortalConfig,
)

class TestDeveloperPortalConfig:
    def test_create(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDeveloperPortalConfig()
        config = svc.create("inst-1", PortalConfig(portal_id="p1", title="My API Portal"))
        assert config.title == "My API Portal"
        assert "docs" in config.sections

    def test_invalid_color(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDeveloperPortalConfig()
        with pytest.raises(ValueError, match="Invalid color"):
            svc.create("inst-1", PortalConfig(portal_id="p1", title="Test", primary_color="red"))

    def test_invalid_section(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDeveloperPortalConfig()
        with pytest.raises(ValueError, match="Invalid sections"):
            svc.create("inst-1", PortalConfig(portal_id="p1", title="Test", sections=["bad"]))

    def test_update(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDeveloperPortalConfig()
        svc.create("inst-1", PortalConfig(portal_id="p1", title="Old"))
        config = svc.update("inst-1", "p1", title="New Title", signup_enabled=False)
        assert config.title == "New Title" and config.signup_enabled is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDeveloperPortalConfig()
        svc.create("inst-1", PortalConfig(portal_id="p1", title="Test"))
        assert len(svc.list_portals("inst-2")) == 0
