import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_response_cache import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCache, CacheConfig,
)

class TestEndpointResponseCache:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_put_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCache()
        svc.configure("inst-1", CacheConfig(endpoint_path="/api/users", ttl_seconds=60))
        svc.put("inst-1", "/api/users", "GET", {}, '{"data":[]}', 200, self._now())
        lookup = svc.get("inst-1", "/api/users", "GET", {}, self._now() + timedelta(seconds=30))
        assert lookup.hit and lookup.entry.status_code == 200

    def test_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCache()
        svc.configure("inst-1", CacheConfig(endpoint_path="/api", ttl_seconds=10))
        svc.put("inst-1", "/api", "GET", {}, "body", 200, self._now())
        lookup = svc.get("inst-1", "/api", "GET", {}, self._now() + timedelta(seconds=15))
        assert not lookup.hit

    def test_vary_by(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCache()
        svc.configure("inst-1", CacheConfig(endpoint_path="/api", ttl_seconds=60, vary_by=["Accept-Language"]))
        svc.put("inst-1", "/api", "GET", {"Accept-Language": "en"}, "english", 200, self._now())
        svc.put("inst-1", "/api", "GET", {"Accept-Language": "ja"}, "japanese", 200, self._now())
        en = svc.get("inst-1", "/api", "GET", {"Accept-Language": "en"}, self._now())
        ja = svc.get("inst-1", "/api", "GET", {"Accept-Language": "ja"}, self._now())
        assert en.entry.response_body == "english" and ja.entry.response_body == "japanese"

    def test_invalidate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCache()
        svc.configure("inst-1", CacheConfig(endpoint_path="/api", ttl_seconds=60))
        svc.put("inst-1", "/api", "GET", {}, "body", 200, self._now())
        removed = svc.invalidate("inst-1", "/api")
        assert removed == 1
        assert not svc.get("inst-1", "/api", "GET", {}, self._now()).hit

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCache()
        svc.configure("inst-1", CacheConfig(endpoint_path="/api", ttl_seconds=60))
        svc.put("inst-1", "/api", "GET", {}, "b", 200, self._now())
        svc.get("inst-1", "/api", "GET", {}, self._now())
        s = svc.stats("inst-1")
        assert s["entries"] == 1 and s["total_hits"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCache()
        svc.configure("inst-1", CacheConfig(endpoint_path="/api", ttl_seconds=60))
        svc.put("inst-1", "/api", "GET", {}, "b", 200, self._now())
        assert svc.stats("inst-2")["entries"] == 0
