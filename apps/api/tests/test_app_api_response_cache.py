"""Tests for App API Response Cache — put, get, expire, hit rate."""

from app.services.app_api_response_cache import AppAPIResponseCache


class TestCache:
    def test_put_get(self):
        c = AppAPIResponseCache()
        c.put("inst-1", "GET:/api/users", 200, '{"data":[]}')
        entry = c.get("inst-1", "GET:/api/users")
        assert entry is not None
        assert entry.status_code == 200

    def test_miss(self):
        c = AppAPIResponseCache()
        assert c.get("inst-1", "missing") is None

    def test_expired(self):
        c = AppAPIResponseCache()
        c.put("inst-1", "key", 200, "{}", ttl_seconds=0)
        assert c.get("inst-1", "key") is None


class TestHitRate:
    def test_rate(self):
        c = AppAPIResponseCache()
        c.put("inst-1", "k1", 200, "{}")
        c.get("inst-1", "k1")  # hit
        c.get("inst-1", "k2")  # miss
        assert c.hit_rate() == 50.0


class TestInvalidate:
    def test_invalidate(self):
        c = AppAPIResponseCache()
        c.put("inst-1", "k1", 200, "{}")
        assert c.invalidate("inst-1", "k1") is True
        assert c.get("inst-1", "k1") is None


class TestIsolation:
    def test_cross(self):
        c = AppAPIResponseCache()
        c.put("inst-1", "k1", 200, "{}")
        assert c.get("inst-2", "k1") is None
