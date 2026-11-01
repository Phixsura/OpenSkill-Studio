"""Tests for App Sliding Window Rate Limiter — counting, reset, cleanup."""

import pytest

from app.services.app_sliding_window import AppSlidingWindowLimiter


class TestConfig:
    def test_invalid_limit(self):
        with pytest.raises(ValueError, match="limit"):
            AppSlidingWindowLimiter(limit=0)

    def test_invalid_window(self):
        with pytest.raises(ValueError, match="window_seconds"):
            AppSlidingWindowLimiter(window_seconds=0)


class TestHit:
    def test_first_hit_allowed(self):
        l = AppSlidingWindowLimiter(limit=5, window_seconds=60)
        r = l.hit("k1", now=1000.0)
        assert r.allowed is True
        assert r.count == 1
        assert r.remaining == 4

    def test_hits_up_to_limit(self):
        l = AppSlidingWindowLimiter(limit=3, window_seconds=60)
        for i in range(3):
            r = l.hit("k1", now=1000.0 + i)
        assert r.allowed is True
        assert r.remaining == 0

    def test_hit_over_limit(self):
        l = AppSlidingWindowLimiter(limit=3, window_seconds=60)
        for i in range(3):
            l.hit("k1", now=1000.0 + i)
        r = l.hit("k1", now=1003.0)
        assert r.allowed is False
        assert r.count == 3
        assert r.remaining == 0

    def test_window_slides(self):
        l = AppSlidingWindowLimiter(limit=3, window_seconds=10)
        l.hit("k1", now=1000.0)
        l.hit("k1", now=1001.0)
        l.hit("k1", now=1002.0)
        # After window passes for first hit
        r = l.hit("k1", now=1011.0)
        assert r.allowed is True  # first hit expired


class TestCheck:
    def test_check_does_not_consume(self):
        l = AppSlidingWindowLimiter(limit=3, window_seconds=60)
        l.hit("k1", now=1000.0)
        r1 = l.check("k1", now=1000.0)
        r2 = l.check("k1", now=1000.0)
        assert r1.count == r2.count == 1

    def test_check_empty_key(self):
        l = AppSlidingWindowLimiter(limit=5, window_seconds=60)
        r = l.check("k1", now=1000.0)
        assert r.allowed is True
        assert r.count == 0
        assert r.remaining == 5


class TestResetAt:
    def test_reset_at_value(self):
        l = AppSlidingWindowLimiter(limit=3, window_seconds=10)
        l.hit("k1", now=1000.0)
        l.hit("k1", now=1005.0)
        r = l.hit("k1", now=1008.0)
        assert r.reset_at == 1010.0  # first hit + window


class TestReset:
    def test_reset_clears(self):
        l = AppSlidingWindowLimiter(limit=3, window_seconds=60)
        l.hit("k1", now=1000.0)
        l.hit("k1", now=1001.0)
        l.reset("k1")
        assert l.get_count("k1", now=1002.0) == 0


class TestGetCount:
    def test_count(self):
        l = AppSlidingWindowLimiter(limit=10, window_seconds=60)
        l.hit("k1", now=1000.0)
        l.hit("k1", now=1001.0)
        assert l.get_count("k1", now=1002.0) == 2

    def test_count_after_expiry(self):
        l = AppSlidingWindowLimiter(limit=10, window_seconds=5)
        l.hit("k1", now=1000.0)
        assert l.get_count("k1", now=1006.0) == 0


class TestCleanup:
    def test_cleanup_expired_keys(self):
        l = AppSlidingWindowLimiter(limit=10, window_seconds=5)
        l.hit("k1", now=1000.0)
        l.hit("k2", now=1000.0)
        count = l.cleanup(now=1006.0)
        assert count == 2

    def test_cleanup_keeps_active(self):
        l = AppSlidingWindowLimiter(limit=10, window_seconds=60)
        l.hit("k1", now=1000.0)
        count = l.cleanup(now=1001.0)
        assert count == 0


class TestKeyIsolation:
    def test_independent_keys(self):
        l = AppSlidingWindowLimiter(limit=2, window_seconds=60)
        l.hit("k1", now=1000.0)
        l.hit("k1", now=1001.0)
        r = l.hit("k2", now=1002.0)
        assert r.allowed is True
        assert r.count == 1
