from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_response_cache import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseCache

class TestResponseCache:
    def test_put_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseCache()
        svc.put("inst-1", "c1", "/users", "GET", 200, '{"data":[]}', ttl_s=3600)
        entry = svc.get("inst-1", "c1", "/users", "GET")
        assert entry is not None and entry.hits == 1

    def test_cache_miss(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseCache()
        assert svc.get("inst-1", "c1", "/nope", "GET") is None

    def test_invalidate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseCache()
        svc.put("inst-1", "c1", "/api", "GET", 200, "{}")
        assert svc.invalidate("inst-1", "c1", "/api", "GET") is True
        assert svc.get("inst-1", "c1", "/api", "GET") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseCache()
        svc.put("inst-1", "c1", "/api", "GET", 200, "{}")
        assert svc.cache_size("inst-2") == 0
