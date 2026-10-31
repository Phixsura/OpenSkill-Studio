from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_endpoint_cache_invalidator import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointCacheInvalidator

class TestEndpointCacheInvalidator:
    def test_cache_and_hit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointCacheInvalidator()
        svc.cache_response("inst-1", "/users", "GET", ttl_s=3600)
        entry = svc.check_cache("inst-1", "GET", "/users")
        assert entry is not None and entry.hit_count == 1

    def test_invalidate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointCacheInvalidator()
        svc.cache_response("inst-1", "/users", "GET")
        svc.cache_response("inst-1", "/users/123", "GET")
        event = svc.invalidate("inst-1", "/users", "Data updated")
        assert event.invalidated_count == 2
        assert svc.check_cache("inst-1", "GET", "/users") is None

    def test_wildcard_invalidation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointCacheInvalidator()
        svc.cache_response("inst-1", "/a", "GET")
        svc.cache_response("inst-1", "/b", "GET")
        event = svc.invalidate("inst-1", "*")
        assert event.invalidated_count == 2

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointCacheInvalidator()
        svc.cache_response("inst-1", "/api", "GET", ttl_s=9999)
        svc.check_cache("inst-1", "GET", "/api")
        stats = svc.cache_stats("inst-1")
        assert stats["cached_entries"] == 1 and stats["total_hits"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointCacheInvalidator()
        svc.cache_response("inst-1", "/api", "GET")
        assert svc.cache_stats("inst-2")["cached_entries"] == 0
