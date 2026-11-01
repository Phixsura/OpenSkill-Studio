"""Tests for App Response Cache — get/put, TTL, ETag, stats."""

import pytest

from app.services.app_response_cache import AppResponseCache


class TestMakeKey:
    def test_deterministic(self):
        c = AppResponseCache()
        k1 = c.make_key("GET", "/api/users")
        k2 = c.make_key("GET", "/api/users")
        assert k1 == k2

    def test_different_methods(self):
        c = AppResponseCache()
        assert c.make_key("GET", "/api") != c.make_key("POST", "/api")

    def test_with_params(self):
        c = AppResponseCache()
        k1 = c.make_key("GET", "/api", {"page": 1})
        k2 = c.make_key("GET", "/api", {"page": 2})
        assert k1 != k2


class TestGetPut:
    def test_cache_hit(self):
        c = AppResponseCache()
        key = c.make_key("GET", "/api/users")
        c.put("inst-1", key, 200, '{"data":[]}', now=1000.0)
        entry = c.get("inst-1", key, now=1000.0)
        assert entry is not None
        assert entry.status_code == 200

    def test_cache_miss(self):
        c = AppResponseCache()
        assert c.get("inst-1", "nonexistent") is None

    def test_expired(self):
        c = AppResponseCache(default_ttl_seconds=60)
        key = c.make_key("GET", "/api")
        c.put("inst-1", key, 200, "body", now=1000.0)
        assert c.get("inst-1", key, now=1061.0) is None

    def test_custom_ttl(self):
        c = AppResponseCache(default_ttl_seconds=300)
        key = c.make_key("GET", "/api")
        c.put("inst-1", key, 200, "body", ttl=5, now=1000.0)
        assert c.get("inst-1", key, now=1006.0) is None


class TestInvalidate:
    def test_invalidate(self):
        c = AppResponseCache()
        key = c.make_key("GET", "/api")
        c.put("inst-1", key, 200, "body")
        assert c.invalidate("inst-1", key) is True
        assert c.get("inst-1", key) is None

    def test_invalidate_nonexistent(self):
        c = AppResponseCache()
        assert c.invalidate("inst-1", "nope") is False


class TestETag:
    def test_etag_generated(self):
        c = AppResponseCache()
        key = c.make_key("GET", "/api")
        entry = c.put("inst-1", key, 200, "body")
        assert len(entry.etag) > 0

    def test_check_etag_match(self):
        c = AppResponseCache()
        key = c.make_key("GET", "/api")
        entry = c.put("inst-1", key, 200, "body")
        assert c.check_etag("inst-1", key, entry.etag) is True

    def test_check_etag_mismatch(self):
        c = AppResponseCache()
        key = c.make_key("GET", "/api")
        c.put("inst-1", key, 200, "body")
        assert c.check_etag("inst-1", key, "wrong") is False


class TestStats:
    def test_stats(self):
        c = AppResponseCache()
        key = c.make_key("GET", "/api")
        c.put("inst-1", key, 200, "body")
        c.get("inst-1", key)  # hit
        c.get("inst-1", "miss")  # miss
        s = c.stats()
        assert s["hits"] == 1
        assert s["misses"] == 1
        assert s["hit_rate"] == 50.0


class TestIsolation:
    def test_cross_installation(self):
        c = AppResponseCache()
        key = c.make_key("GET", "/api")
        c.put("inst-1", key, 200, "body")
        assert c.get("inst-2", key) is None
