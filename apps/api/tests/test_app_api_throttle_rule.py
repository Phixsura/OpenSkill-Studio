"""Tests for App API Throttle Rule — check, window, retry_after."""

import pytest
from app.services.app_api_throttle_rule import AppAPIThrottleRule


class TestAdd:
    def test_add(self):
        t = AppAPIThrottleRule()
        r = t.add_rule("inst-1", "r1", "/api/*", 10, 60)
        assert r.max_requests == 10


class TestThrottle:
    def test_allowed(self):
        t = AppAPIThrottleRule()
        t.add_rule("inst-1", "r1", "/api/*", 5, 60)
        result = t.check_and_record("inst-1", "r1", "consumer-a")
        assert result["allowed"] is True
        assert result["remaining"] == 4

    def test_throttled(self):
        t = AppAPIThrottleRule()
        t.add_rule("inst-1", "r1", "/api/*", 2, 60)
        t.check_and_record("inst-1", "r1", "consumer-a")
        t.check_and_record("inst-1", "r1", "consumer-a")
        result = t.check_and_record("inst-1", "r1", "consumer-a")
        assert result["allowed"] is False
        assert result["retry_after"] > 0

    def test_per_consumer(self):
        t = AppAPIThrottleRule()
        t.add_rule("inst-1", "r1", "/api/*", 1, 60)
        t.check_and_record("inst-1", "r1", "a")
        result = t.check_and_record("inst-1", "r1", "b")
        assert result["allowed"] is True  # different consumer


class TestIsolation:
    def test_cross(self):
        t = AppAPIThrottleRule()
        t.add_rule("inst-1", "r1", "/api/*", 10, 60)
        assert t.list_rules("inst-2") == []
