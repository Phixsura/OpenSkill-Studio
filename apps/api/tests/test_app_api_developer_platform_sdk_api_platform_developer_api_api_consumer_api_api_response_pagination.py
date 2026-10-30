import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_response_pagination import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponsePagination, PaginationConfig,
)

class TestResponsePagination:
    def test_basic_pagination(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponsePagination()
        svc.configure("inst-1", PaginationConfig(consumer_id="c1", default_page_size=10))
        items = list(range(25))
        result = svc.paginate("inst-1", "c1", items, page=1)
        assert len(result.data) == 10
        assert result.total == 25
        assert result.total_pages == 3
        assert result.has_next is True
        assert result.has_prev is False

    def test_last_page(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponsePagination()
        svc.configure("inst-1", PaginationConfig(consumer_id="c1", default_page_size=10))
        result = svc.paginate("inst-1", "c1", list(range(25)), page=3)
        assert len(result.data) == 5
        assert result.has_next is False
        assert result.has_prev is True

    def test_max_page_size_enforced(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponsePagination()
        svc.configure("inst-1", PaginationConfig(consumer_id="c1", default_page_size=10, max_page_size=50))
        result = svc.paginate("inst-1", "c1", list(range(200)), page_size=100)
        assert len(result.data) == 50

    def test_invalid_style(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponsePagination()
        with pytest.raises(ValueError, match="Invalid style"):
            svc.configure("inst-1", PaginationConfig(consumer_id="c1", style="random"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponsePagination()
        svc.configure("inst-1", PaginationConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
