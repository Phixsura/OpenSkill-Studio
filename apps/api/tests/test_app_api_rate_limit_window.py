"""Tests for App API Rate Limit Window — check, throttle, reset."""

from app.services.app_api_rate_limit_window import AppAPIRateLimitWindow


class TestCheck:
    def test_allowed(self):
        r = AppAPIRateLimitWindow(max_requests=5, window_seconds=60)
        result = r.check("inst-1", "consumer-a")
        assert result["allowed"] is True
        assert result["remaining"] == 4

    def test_throttled(self):
        r = AppAPIRateLimitWindow(max_requests=2, window_seconds=60)
        r.check("inst-1", "a")
        r.check("inst-1", "a")
        result = r.check("inst-1", "a")
        assert result["allowed"] is False
        assert result["remaining"] == 0

    def test_per_consumer(self):
        r = AppAPIRateLimitWindow(max_requests=1, window_seconds=60)
        r.check("inst-1", "a")
        result = r.check("inst-1", "b")
        assert result["allowed"] is True


class TestReset:
    def test_reset(self):
        r = AppAPIRateLimitWindow(max_requests=1, window_seconds=60)
        r.check("inst-1", "a")
        r.reset("inst-1", "a")
        assert r.current_usage("inst-1", "a") == 0


class TestIsolation:
    def test_cross(self):
        r = AppAPIRateLimitWindow(max_requests=1, window_seconds=60)
        r.check("inst-1", "a")
        result = r.check("inst-2", "a")
        assert result["allowed"] is True
