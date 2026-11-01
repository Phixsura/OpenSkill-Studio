"""Tests for Consumer API Request Throttle service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_request_throttle import (
    RequestThrottle, ThrottleConfig,
)


class TestRequestThrottle:
    def test_allow_under_limit(self):
        svc = RequestThrottle()
        svc.configure(ThrottleConfig("c1", base_rate=10))
        result = svc.check("c1", current_time=100.0)
        assert result["allowed"] is True
        assert result["remaining"] == 9

    def test_throttle_over_limit(self):
        svc = RequestThrottle()
        svc.configure(ThrottleConfig("c1", base_rate=3, adaptive=False))
        for t in range(3):
            svc.check("c1", current_time=100.0)
        result = svc.check("c1", current_time=100.0)
        assert result["allowed"] is False
        assert result["reason"] == "throttled"

    def test_window_reset(self):
        svc = RequestThrottle()
        svc.configure(ThrottleConfig("c1", base_rate=2, window_seconds=10.0, adaptive=False))
        svc.check("c1", current_time=100.0)
        svc.check("c1", current_time=100.0)
        # Window expired
        result = svc.check("c1", current_time=115.0)
        assert result["allowed"] is True

    def test_backpressure(self):
        svc = RequestThrottle()
        svc.configure(ThrottleConfig("c1", base_rate=10, backpressure_threshold=0.5))
        for _ in range(5):
            svc.check("c1", current_time=100.0)
        result = svc.check("c1", current_time=100.0)
        assert result["backpressure"] is True

    def test_adaptive_reduces_rate(self):
        svc = RequestThrottle()
        svc.configure(ThrottleConfig("c1", base_rate=10, backpressure_threshold=0.5))
        for _ in range(6):
            svc.check("c1", current_time=100.0)
        status = svc.get_status("c1")
        assert status["effective_rate"] < 10

    def test_no_config_allows(self):
        svc = RequestThrottle()
        result = svc.check("unknown")
        assert result["allowed"] is True
        assert result["reason"] == "no_config"

    def test_non_adaptive(self):
        svc = RequestThrottle()
        svc.configure(ThrottleConfig("c1", base_rate=5, adaptive=False))
        for _ in range(4):
            svc.check("c1", current_time=100.0)
        status = svc.get_status("c1")
        assert status["effective_rate"] == 5  # unchanged

    def test_reset(self):
        svc = RequestThrottle()
        svc.configure(ThrottleConfig("c1", base_rate=5))
        for _ in range(5):
            svc.check("c1", current_time=100.0)
        svc.reset("c1")
        result = svc.check("c1", current_time=200.0)
        assert result["allowed"] is True

    def test_stats(self):
        svc = RequestThrottle()
        svc.configure(ThrottleConfig("c1", base_rate=2, adaptive=False))
        svc.check("c1", current_time=100.0)
        svc.check("c1", current_time=100.0)
        svc.check("c1", current_time=100.0)  # throttled
        stats = svc.get_stats()
        assert stats["total_throttled"] == 1

    def test_invalid_rate(self):
        svc = RequestThrottle()
        with pytest.raises(ValueError):
            svc.configure(ThrottleConfig("c1", base_rate=0))

    def test_isolation(self):
        a, b = RequestThrottle(), RequestThrottle()
        a.configure(ThrottleConfig("c1", base_rate=5))
        assert b.check("c1")["reason"] == "no_config"
