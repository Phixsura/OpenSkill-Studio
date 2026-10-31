import pytest
from app.services.app_api_developer_platform_sdk_api_developer_portal_navigation import AppAPIDeveloperPlatformSDKApiDeveloperPortalNavigation

class TestPortalNavigation:
    def test_add_item(self):
        n = AppAPIDeveloperPlatformSDKApiDeveloperPortalNavigation()
        item = n.add_item("inst-1", "docs", "Documentation", "/docs", "📚", order=1)
        assert item.label == "Documentation"

    def test_top_level(self):
        n = AppAPIDeveloperPlatformSDKApiDeveloperPortalNavigation()
        n.add_item("inst-1", "docs", "Docs", "/docs", order=2)
        n.add_item("inst-1", "home", "Home", "/", order=1)
        n.add_item("inst-1", "auth", "Auth Guide", "/docs/auth", parent_id="docs")
        top = n.top_level("inst-1")
        assert len(top) == 2
        assert top[0].item_id == "home"

    def test_children(self):
        n = AppAPIDeveloperPlatformSDKApiDeveloperPortalNavigation()
        n.add_item("inst-1", "docs", "Docs", "/docs")
        n.add_item("inst-1", "auth", "Auth", "/docs/auth", parent_id="docs", order=1)
        n.add_item("inst-1", "webhooks", "Webhooks", "/docs/webhooks", parent_id="docs", order=2)
        children = n.children_of("inst-1", "docs")
        assert len(children) == 2

    def test_hidden(self):
        n = AppAPIDeveloperPlatformSDKApiDeveloperPortalNavigation()
        n.add_item("inst-1", "secret", "Secret", "/secret")
        n.toggle_visibility("inst-1", "secret", False)
        assert len(n.top_level("inst-1")) == 0

    def test_isolation(self):
        n = AppAPIDeveloperPlatformSDKApiDeveloperPortalNavigation()
        n.add_item("inst-1", "home", "Home", "/")
        assert len(n.all_items("inst-2")) == 0
