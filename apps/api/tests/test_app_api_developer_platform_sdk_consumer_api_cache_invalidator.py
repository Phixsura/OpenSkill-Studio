"""Tests for Endpoint Cache Invalidator service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_cache_invalidator import CacheInvalidator


class TestCacheInvalidator:
    def test_register_and_get(self):
        svc = CacheInvalidator()
        svc.register("k1", ["users", "api"])
        entry = svc.get_entry("k1")
        assert entry is not None
        assert "users" in entry["tags"]

    def test_invalidate_key(self):
        svc = CacheInvalidator()
        svc.register("k1", ["t1"])
        result = svc.invalidate_key("k1")
        assert result["invalidated"] == 1
        assert svc.get_entry("k1") is None

    def test_invalidate_tag(self):
        svc = CacheInvalidator()
        svc.register("k1", ["users"])
        svc.register("k2", ["users"])
        svc.register("k3", ["orders"])
        result = svc.invalidate_tag("users")
        assert result["invalidated"] == 2
        assert svc.get_entry("k1") is None
        assert svc.get_entry("k3") is not None

    def test_cascade_invalidation(self):
        svc = CacheInvalidator()
        svc.register("k1", ["users"])
        svc.register("k2", ["user_list"])
        svc.add_cascade("user_list", "users")
        result = svc.invalidate_tag("users")
        assert result["invalidated"] == 2
        assert svc.get_entry("k2") is None

    def test_cascade_cycle_protection(self):
        svc = CacheInvalidator()
        svc.register("k1", ["a"])
        svc.register("k2", ["b"])
        svc.add_cascade("b", "a")
        svc.add_cascade("a", "b")
        # Should not infinite loop
        result = svc.invalidate_tag("a")
        assert result["invalidated"] >= 1

    def test_self_cascade_rejected(self):
        svc = CacheInvalidator()
        with pytest.raises(ValueError):
            svc.add_cascade("x", "x")

    def test_get_keys_by_tag(self):
        svc = CacheInvalidator()
        svc.register("k1", ["api"])
        svc.register("k2", ["api"])
        keys = svc.get_keys_by_tag("api")
        assert "k1" in keys and "k2" in keys

    def test_stats(self):
        svc = CacheInvalidator()
        svc.register("k1", ["t1", "t2"])
        svc.register("k2", ["t2"])
        stats = svc.get_stats()
        assert stats["total_entries"] == 2
        assert stats["total_tags"] == 2

    def test_clear_all(self):
        svc = CacheInvalidator()
        svc.register("k1", ["t"])
        svc.register("k2", ["t"])
        result = svc.clear_all()
        assert result["cleared"] == 2
        assert svc.get_stats()["total_entries"] == 0

    def test_invalidate_nonexistent(self):
        svc = CacheInvalidator()
        assert svc.invalidate_key("nope")["invalidated"] == 0

    def test_isolation(self):
        a, b = CacheInvalidator(), CacheInvalidator()
        a.register("k1", ["t"])
        assert b.get_entry("k1") is None
