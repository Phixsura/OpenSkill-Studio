import pytest
from app.services.app_api_developer_api_api_developer_portal_theme import AppAPIDeveloperAPIApiDeveloperPortalTheme

class TestPortalTheme:
    def test_set_theme(self):
        t = AppAPIDeveloperAPIApiDeveloperPortalTheme()
        th = t.set_theme("inst-1", "#FF5733", "#33FF57", portal_title="My API")
        assert th.portal_title == "My API"

    def test_invalid_color(self):
        t = AppAPIDeveloperAPIApiDeveloperPortalTheme()
        with pytest.raises(ValueError, match="hex"):
            t.set_theme("inst-1", "red", "#000000")

    def test_https_required(self):
        t = AppAPIDeveloperAPIApiDeveloperPortalTheme()
        with pytest.raises(ValueError, match="HTTPS"):
            t.set_theme("inst-1", "#000000", "#FFFFFF", logo_url="http://bad.com/logo.png")

    def test_default_theme(self):
        t = AppAPIDeveloperAPIApiDeveloperPortalTheme()
        th = t.get_theme("inst-1")
        assert th.primary_color == "#3B82F6"
        assert t.has_custom_theme("inst-1") is False

    def test_css_too_large(self):
        t = AppAPIDeveloperAPIApiDeveloperPortalTheme()
        with pytest.raises(ValueError, match="too large"):
            t.set_theme("inst-1", "#000000", "#FFFFFF", custom_css="x" * 20000)
