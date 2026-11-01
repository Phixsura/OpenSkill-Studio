"""Tests for Endpoint Response Cache service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_response_cache import ResponseCache


class TestResponseCache:
    def test_put_and_get(self):
        svc = ResponseCache()
        svc.put("k1", {"data": "hello"}, current_time=100)
        result = svc.get("k1", current_time=100)
        assert result is not None
        assert result["body"] == {"data": "hello"}

    def test_miss(self):
        svc = ResponseCache()
        assert svc.get("missing") is None

    def test_ttl_expiry(self):
        svc = ResponseCache()
        svc.put("k1", "data", ttl_seconds=10, current_time=100)
        assert svc.get("k1", current_time=105) is not None
        assert svc.get("k1", current_time=115) is None

    def test_lru_eviction(self):
        svc = ResponseCache()
        svc.configure(max_entries=2)
        svc.put("k1", "a")
        svc.put("k2", "b")
        svc.put("k3", "c")  # should evict k1
        assert svc.get("k1") is None
        assert svc.get("k2") is not None

    def test_hit_count(self):
        svc = ResponseCache()
        svc.put("k1", "data")
        svc.get("k1")
        svc.get("k1")
        result = svc.get("k1")
        assert result["hit_count"] == 3

    def test_invalidate(self):
        svc = ResponseCache()
        svc.put("k1", "data")
        result = svc.invalidate("k1")
        assert result["invalidated"] is True
        assert svc.get("k1") is None

    def test_invalidate_pattern(self):
        svc = ResponseCache()
        svc.put("users:1", "a")
        svc.put("users:2", "b")
        svc.put("orders:1", "c")
        result = svc.invalidate_pattern("users:")
        assert result["invalidated"] == 2

    def test_stats(self):
        svc = ResponseCache()
        svc.put("k1", "data")
        svc.get("k1")
        svc.get("missing")
        stats = svc.get_stats()
        assert stats["total_hits"] == 1
        assert stats["total_misses"] == 1
        assert stats["hit_rate"] == 50.0

    def test_clear(self):
        svc = ResponseCache()
        svc.put("k1", "a")
        svc.put("k2", "b")
        result = svc.clear()
        assert result["cleared"] == 2
        assert svc.get_stats()["entries"] == 0

    def test_isolation(self):
        a, b = ResponseCache(), ResponseCache()
        a.put("k1", "data")
        assert b.get("k1") is None
