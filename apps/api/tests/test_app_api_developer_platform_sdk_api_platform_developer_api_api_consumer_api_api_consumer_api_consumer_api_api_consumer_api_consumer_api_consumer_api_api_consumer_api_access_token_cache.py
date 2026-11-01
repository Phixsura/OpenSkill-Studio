import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_access_token_cache import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCache,
)

class TestAccessTokenCache:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_put_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCache()
        svc.put("inst-1", "hash123", "c1", ["read:users"], self._now())
        entry = svc.get("inst-1", "hash123", self._now() + timedelta(seconds=10))
        assert entry is not None and entry.consumer_id == "c1"

    def test_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCache(ttl_seconds=60)
        svc.put("inst-1", "hash123", "c1", [], self._now())
        assert svc.get("inst-1", "hash123", self._now() + timedelta(seconds=120)) is None

    def test_invalidate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCache()
        svc.put("inst-1", "hash123", "c1", [], self._now())
        assert svc.invalidate("inst-1", "hash123")
        assert svc.get("inst-1", "hash123", self._now()) is None

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCache()
        svc.put("inst-1", "h1", "c1", [], self._now())
        svc.get("inst-1", "h1", self._now())  # hit
        svc.get("inst-1", "missing", self._now())  # miss
        stats = svc.get_stats("inst-1")
        assert stats.hit_count == 1 and stats.miss_count == 1 and stats.hit_rate_pct == 50.0

    def test_eviction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCache(max_entries=2)
        svc.put("inst-1", "h1", "c1", [], self._now())
        svc.put("inst-1", "h2", "c2", [], self._now() + timedelta(seconds=1))
        svc.put("inst-1", "h3", "c3", [], self._now() + timedelta(seconds=2))  # evicts h1
        assert svc.get("inst-1", "h1", self._now()) is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCache()
        svc.put("inst-1", "h1", "c1", [], self._now())
        assert svc.get("inst-2", "h1", self._now()) is None
