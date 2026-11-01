import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_developer_portal import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortal, PortalConfig, PortalPage,
)

class TestConsumerApiDeveloperPortal:
    def test_set_and_get_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortal()
        svc.set_config("inst-1", PortalConfig(portal_id="p1", title="My API Portal"))
        cfg = svc.get_config("inst-1", "p1")
        assert cfg.title == "My API Portal" and cfg.show_playground

    def test_add_page(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortal()
        svc.set_config("inst-1", PortalConfig(portal_id="p1", title="Portal"))
        svc.add_page("inst-1", "p1", PortalPage(page_id="pg1", title="Getting Started", slug="getting-started", content="# Welcome", published=True))
        pages = svc.list_pages("inst-1", published_only=True)
        assert len(pages) == 1

    def test_get_by_slug(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortal()
        svc.set_config("inst-1", PortalConfig(portal_id="p1", title="Portal"))
        svc.add_page("inst-1", "p1", PortalPage(page_id="pg1", title="Auth", slug="auth-guide", content="How to auth"))
        page = svc.get_page_by_slug("inst-1", "auth-guide")
        assert page is not None and page.title == "Auth"

    def test_draft_filtered(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortal()
        svc.set_config("inst-1", PortalConfig(portal_id="p1", title="Portal"))
        svc.add_page("inst-1", "p1", PortalPage(page_id="pg1", title="Draft", slug="draft", content="WIP", published=False))
        assert len(svc.list_pages("inst-1", published_only=True)) == 0

    def test_invalid_color(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortal()
        with pytest.raises(ValueError, match="hex color"):
            svc.set_config("inst-1", PortalConfig(portal_id="p1", title="X", primary_color="red"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortal()
        svc.set_config("inst-1", PortalConfig(portal_id="p1", title="Portal"))
        assert svc.get_config("inst-2", "p1") is None
