from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_cache_key_builder import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCacheKeyBuilder, CacheKeyConfig,
)

class TestCacheKeyBuilder:
    def test_deterministic(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCacheKeyBuilder()
        k1 = svc.build_key("inst-1", "c1", "GET", "/users", {"page": "1"})
        k2 = svc.build_key("inst-1", "c1", "GET", "/users", {"page": "1"})
        assert k1 == k2

    def test_different_params_different_key(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCacheKeyBuilder()
        k1 = svc.build_key("inst-1", "c1", "GET", "/users", {"page": "1"})
        k2 = svc.build_key("inst-1", "c1", "GET", "/users", {"page": "2"})
        assert k1 != k2

    def test_ignore_params(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCacheKeyBuilder()
        svc.configure("inst-1", CacheKeyConfig(consumer_id="c1", ignore_params=["_t", "nonce"]))
        k1 = svc.build_key("inst-1", "c1", "GET", "/api", {"page": "1", "_t": "123"})
        k2 = svc.build_key("inst-1", "c1", "GET", "/api", {"page": "1", "_t": "456"})
        assert k1 == k2

    def test_include_headers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCacheKeyBuilder()
        svc.configure("inst-1", CacheKeyConfig(consumer_id="c1", include_headers=["Accept-Language"]))
        k1 = svc.build_key("inst-1", "c1", "GET", "/api", headers={"Accept-Language": "en"})
        k2 = svc.build_key("inst-1", "c1", "GET", "/api", headers={"Accept-Language": "fr"})
        assert k1 != k2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCacheKeyBuilder()
        svc.configure("inst-1", CacheKeyConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
