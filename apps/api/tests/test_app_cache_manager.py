"""Tests for App Cache Manager — get/set, TTL, LRU eviction, stats."""

import pytest

from app.services.app_cache_manager import AppCacheManager


class TestGetSet:
    def test_set_and_get(self):
        c = AppCacheManager()
        c.set("inst-1", "k1", {"data": "hello"})
        assert c.get("inst-1", "k1") == {"data": "hello"}

    def test_miss_returns_none(self):
        c = AppCacheManager()
        assert c.get("inst-1", "nope") is None

    def test_overwrite(self):
        c = AppCacheManager()
        c.set("inst-1", "k1", "v1")
        c.set("inst-1", "k1", "v2")
        assert c.get("inst-1", "k1") == "v2"

    def test_missing_key(self):
        c = AppCacheManager()
        with pytest.raises(ValueError, match="key"):
            c.set("inst-1", "", "val")

    def test_missing_installation_id(self):
        c = AppCacheManager()
        with pytest.raises(ValueError, match="installation_id"):
            c.set("", "k1", "val")


class TestTTL:
    def test_expired_returns_none(self):
        c = AppCacheManager(default_ttl_seconds=10)
        c.set("inst-1", "k1", "val", now=1000.0)
        assert c.get("inst-1", "k1", now=1011.0) is None

    def test_not_expired(self):
        c = AppCacheManager(default_ttl_seconds=10)
        c.set("inst-1", "k1", "val", now=1000.0)
        assert c.get("inst-1", "k1", now=1005.0) == "val"

    def test_custom_ttl(self):
        c = AppCacheManager(default_ttl_seconds=300)
        c.set("inst-1", "k1", "val", ttl_seconds=5, now=1000.0)
        assert c.get("inst-1", "k1", now=1006.0) is None


class TestLRU:
    def test_evicts_lru(self):
        c = AppCacheManager(max_size=3)
        c.set("inst-1", "k1", "v1", now=1000.0)
        c.set("inst-1", "k2", "v2", now=1001.0)
        c.set("inst-1", "k3", "v3", now=1002.0)
        c.set("inst-1", "k4", "v4", now=1003.0)  # evicts k1
        assert c.get("inst-1", "k1", now=1003.0) is None
        assert c.get("inst-1", "k2", now=1003.0) is not None

    def test_access_refreshes_lru(self):
        c = AppCacheManager(max_size=3)
        c.set("inst-1", "k1", "v1", now=1000.0)
        c.set("inst-1", "k2", "v2", now=1001.0)
        c.set("inst-1", "k3", "v3", now=1002.0)
        c.get("inst-1", "k1", now=1003.0)  # refresh k1
        c.set("inst-1", "k4", "v4", now=1004.0)  # evicts k2 (now LRU)
        assert c.get("inst-1", "k1", now=1004.0) is not None
        assert c.get("inst-1", "k2", now=1004.0) is None


class TestDelete:
    def test_delete_existing(self):
        c = AppCacheManager()
        c.set("inst-1", "k1", "v1")
        assert c.delete("inst-1", "k1") is True
        assert c.get("inst-1", "k1", now=1003.0) is None

    def test_delete_nonexistent(self):
        c = AppCacheManager()
        assert c.delete("inst-1", "nope") is False


class TestInvalidatePrefix:
    def test_prefix_invalidation(self):
        c = AppCacheManager()
        c.set("inst-1", "user:1", "a")
        c.set("inst-1", "user:2", "b")
        c.set("inst-1", "config:x", "c")
        count = c.invalidate_prefix("inst-1", "user:")
        assert count == 2
        assert c.get("inst-1", "user:1") is None
        assert c.get("inst-1", "config:x") == "c"


class TestExists:
    def test_exists(self):
        c = AppCacheManager()
        c.set("inst-1", "k1", "v1")
        assert c.exists("inst-1", "k1") is True
        assert c.exists("inst-1", "nope") is False


class TestStats:
    def test_hit_miss_counts(self):
        c = AppCacheManager()
        c.set("inst-1", "k1", "v1")
        c.get("inst-1", "k1")   # hit
        c.get("inst-1", "nope") # miss
        stats = c.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.hit_rate == 50.0

    def test_eviction_count(self):
        c = AppCacheManager(max_size=2)
        c.set("inst-1", "k1", "v1")
        c.set("inst-1", "k2", "v2")
        c.set("inst-1", "k3", "v3")
        assert c.get_stats().evictions == 1


class TestClear:
    def test_clear_all(self):
        c = AppCacheManager()
        c.set("inst-1", "k1", "v1")
        c.set("inst-2", "k2", "v2")
        count = c.clear()
        assert count == 2
        assert c.get_stats().size == 0

    def test_clear_installation(self):
        c = AppCacheManager()
        c.set("inst-1", "k1", "v1")
        c.set("inst-2", "k2", "v2")
        count = c.clear("inst-1")
        assert count == 1
        assert c.get("inst-2", "k2") == "v2"


class TestIsolation:
    def test_cross_installation(self):
        c = AppCacheManager()
        c.set("inst-1", "k1", "v1")
        assert c.get("inst-2", "k1") is None


class TestConfig:
    def test_invalid_max_size(self):
        with pytest.raises(ValueError, match="max_size"):
            AppCacheManager(max_size=0)

    def test_invalid_ttl(self):
        with pytest.raises(ValueError, match="default_ttl"):
            AppCacheManager(default_ttl_seconds=0)
