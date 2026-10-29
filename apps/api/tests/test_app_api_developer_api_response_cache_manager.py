import pytest
from app.services.app_api_developer_api_response_cache_manager import AppAPIDeveloperAPIResponseCacheManager

class TestResponseCacheManager:
    def test_put_get(self):
        m = AppAPIDeveloperAPIResponseCacheManager()
        m.put("inst-1", "k1", "/api/users", 3600, 512)
        e = m.get("inst-1", "k1")
        assert e is not None
        assert e.hit_count == 1

    def test_miss(self):
        m = AppAPIDeveloperAPIResponseCacheManager()
        assert m.get("inst-1", "k1") is None

    def test_expired(self):
        m = AppAPIDeveloperAPIResponseCacheManager()
        m.put("inst-1", "k1", "/api/users", 1)
        e = m._cache[("inst-1", "k1")]
        e.created_at -= 10  # force expired
        assert m.get("inst-1", "k1") is None

    def test_invalidate(self):
        m = AppAPIDeveloperAPIResponseCacheManager()
        m.put("inst-1", "k1", "/api/users", 3600)
        m.put("inst-1", "k2", "/api/users", 3600)
        m.put("inst-1", "k3", "/api/orders", 3600)
        assert m.invalidate("inst-1", "/api/users") == 2

    def test_stats(self):
        m = AppAPIDeveloperAPIResponseCacheManager()
        m.put("inst-1", "k1", "/api/users", 3600, 100)
        m.get("inst-1", "k1")
        m.get("inst-1", "k2")
        s = m.stats("inst-1")
        assert s.hits == 1
        assert s.misses == 1
        assert s.hit_rate_pct == 50.0

    def test_isolation(self):
        m = AppAPIDeveloperAPIResponseCacheManager()
        m.put("inst-1", "k1", "/a", 3600)
        assert m.stats("inst-2").total_entries == 0
