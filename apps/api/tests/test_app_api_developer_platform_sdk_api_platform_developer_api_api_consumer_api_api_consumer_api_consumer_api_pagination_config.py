import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_pagination_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfig, PaginationConfig,
)

class TestConsumerApiPaginationConfig:
    def test_default_resolve(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfig()
        svc.set_config("inst-1", PaginationConfig(consumer_id="c1", default_page_size=25, max_page_size=50))
        params = svc.resolve("inst-1", "c1")
        assert params.page_size == 25 and params.strategy == "cursor"

    def test_capped_at_max(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfig()
        svc.set_config("inst-1", PaginationConfig(consumer_id="c1", default_page_size=20, max_page_size=50))
        params = svc.resolve("inst-1", "c1", requested_size=200)
        assert params.page_size == 50

    def test_build_meta_has_more(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfig()
        svc.set_config("inst-1", PaginationConfig(consumer_id="c1", default_page_size=10))
        meta = svc.build_meta("inst-1", "c1", returned_count=10, next_cursor="abc")
        assert meta.has_more and meta.next_cursor == "abc"

    def test_build_meta_no_more(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfig()
        svc.set_config("inst-1", PaginationConfig(consumer_id="c1", default_page_size=10))
        meta = svc.build_meta("inst-1", "c1", returned_count=5)
        assert not meta.has_more

    def test_invalid_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfig()
        with pytest.raises(ValueError, match="max_page_size"):
            svc.set_config("inst-1", PaginationConfig(consumer_id="c1", default_page_size=50, max_page_size=10))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfig()
        svc.set_config("inst-1", PaginationConfig(consumer_id="c1", default_page_size=30))
        assert svc.get_config("inst-2", "c1") is None
