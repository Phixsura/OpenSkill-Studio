import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_documentation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentation, DocPage,
)

class TestConsumerApiDocumentation:
    def test_create_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentation()
        svc.create_page("inst-1", DocPage(page_id="p1", title="Getting Started", content="# Hello\nWelcome to the API.", category="guide"))
        page = svc.get_page("inst-1", "p1")
        assert page.title == "Getting Started"

    def test_update(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentation()
        svc.create_page("inst-1", DocPage(page_id="p1", title="Draft", content="WIP"))
        svc.update_page("inst-1", "p1", title="Final", published=True)
        page = svc.get_page("inst-1", "p1")
        assert page.title == "Final" and page.published

    def test_list_published(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentation()
        svc.create_page("inst-1", DocPage(page_id="p1", title="A", content="x", published=True))
        svc.create_page("inst-1", DocPage(page_id="p2", title="B", content="y", published=False))
        pages = svc.list_pages("inst-1", published_only=True)
        assert len(pages) == 1

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentation()
        svc.create_page("inst-1", DocPage(page_id="p1", title="Auth Guide", content="How to authenticate"))
        svc.create_page("inst-1", DocPage(page_id="p2", title="Rate Limits", content="Rate limit details"))
        results = svc.search("inst-1", "auth")
        assert len(results) == 1 and results[0].page_id == "p1"

    def test_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentation()
        svc.create_page("inst-1", DocPage(page_id="p1", title="X", content="y"))
        with pytest.raises(ValueError, match="already exists"):
            svc.create_page("inst-1", DocPage(page_id="p1", title="Z", content="w"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentation()
        svc.create_page("inst-1", DocPage(page_id="p1", title="X", content="y"))
        assert len(svc.list_pages("inst-2")) == 0
