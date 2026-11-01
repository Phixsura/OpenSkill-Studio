"""Tests for Consumer Idempotency Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_idempotency import IdempotencyManager


class TestIdempotencyManager:
    def test_store_and_check(self):
        svc = IdempotencyManager()
        svc.store("k1", "c1", 200, {"id": 1}, current_time=100.0)
        result = svc.check("k1", "c1", current_time=200.0)
        assert result["exists"] is True
        assert result["status_code"] == 200
        assert result["response_body"] == {"id": 1}

    def test_check_not_found(self):
        svc = IdempotencyManager()
        result = svc.check("missing", "c1")
        assert result["exists"] is False

    def test_expired_key(self):
        svc = IdempotencyManager()
        svc.store("k1", "c1", 200, "ok", current_time=100.0, ttl=60.0)
        result = svc.check("k1", "c1", current_time=200.0)
        assert result["exists"] is False
        assert result["reason"] == "expired"

    def test_different_consumer(self):
        svc = IdempotencyManager()
        svc.store("k1", "c1", 200, "ok", current_time=100.0)
        result = svc.check("k1", "c2", current_time=100.0)
        assert result["exists"] is False

    def test_delete(self):
        svc = IdempotencyManager()
        svc.store("k1", "c1", 200, "ok")
        assert svc.delete("k1")["deleted"] is True
        assert svc.check("k1", "c1")["exists"] is False

    def test_cleanup_expired(self):
        svc = IdempotencyManager()
        svc.store("k1", "c1", 200, "ok", current_time=100.0, ttl=10.0)
        svc.store("k2", "c1", 200, "ok", current_time=100.0, ttl=1000.0)
        result = svc.cleanup_expired(current_time=200.0)
        assert result["removed"] == 1
        assert result["remaining"] == 1

    def test_eviction(self):
        svc = IdempotencyManager()
        svc.configure(max_records=3)
        svc.store("k1", "c1", 200, "a", current_time=1.0)
        svc.store("k2", "c1", 200, "b", current_time=2.0)
        svc.store("k3", "c1", 200, "c", current_time=3.0)
        svc.store("k4", "c1", 200, "d", current_time=4.0)
        assert svc.check("k1", "c1")["exists"] is False  # evicted
        assert svc.check("k4", "c1")["exists"] is True

    def test_consumer_keys(self):
        svc = IdempotencyManager()
        svc.store("k1", "c1", 200, "a")
        svc.store("k2", "c1", 201, "b")
        svc.store("k3", "c2", 200, "c")
        keys = svc.get_consumer_keys("c1")
        assert len(keys) == 2

    def test_stats(self):
        svc = IdempotencyManager()
        svc.configure(max_records=100)
        svc.store("k1", "c1", 200, "a")
        stats = svc.get_stats()
        assert stats["total_records"] == 1
        assert stats["usage_pct"] == 1.0

    def test_invalid_ttl(self):
        svc = IdempotencyManager()
        with pytest.raises(ValueError):
            svc.configure(default_ttl=0)

    def test_isolation(self):
        a, b = IdempotencyManager(), IdempotencyManager()
        a.store("k1", "c1", 200, "a")
        assert b.check("k1", "c1")["exists"] is False
