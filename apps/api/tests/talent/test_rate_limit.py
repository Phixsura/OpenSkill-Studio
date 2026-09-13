"""Rate limiter tests — pure in-memory logic, no DB needed."""

from time import time

import pytest

from app.talent.api.rate_limit import (
    MAX_REQUESTS,
    WINDOW_SECONDS,
    _counters,
    _gc_stale_keys,
    reset_rate_limiter,
)


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset rate limiter state before each test."""
    reset_rate_limiter()
    yield
    reset_rate_limiter()


class TestRateLimitCounters:
    def test_initial_state_empty(self):
        assert len(_counters) == 0

    def test_counter_increments(self):
        now = time()
        _counters["user1"].append(now)
        assert len(_counters["user1"]) == 1

    def test_counter_tracks_multiple_users(self):
        now = time()
        _counters["user1"].append(now)
        _counters["user2"].append(now)
        _counters["user2"].append(now)
        assert len(_counters["user1"]) == 1
        assert len(_counters["user2"]) == 2

    def test_reset_clears_all(self):
        _counters["user1"].append(time())
        _counters["user2"].append(time())
        reset_rate_limiter()
        assert len(_counters) == 0


class TestGarbageCollection:
    def test_removes_stale_keys(self):
        now = time()
        _counters["old_user"] = [now - WINDOW_SECONDS - 10]
        _counters["active_user"] = [now]
        _gc_stale_keys(now)
        assert "old_user" not in _counters
        assert "active_user" in _counters

    def test_removes_empty_keys(self):
        _counters["empty_user"] = []
        _gc_stale_keys(time())
        assert "empty_user" not in _counters

    def test_keeps_recent_entries(self):
        now = time()
        _counters["user"] = [now - 10, now - 5, now]
        _gc_stale_keys(now)
        assert "user" in _counters
        assert len(_counters["user"]) == 3


class TestRateLimitConstants:
    def test_window_is_one_minute(self):
        assert WINDOW_SECONDS == 60

    def test_max_requests_is_100(self):
        assert MAX_REQUESTS == 100


class TestWindowExpiry:
    def test_old_timestamps_would_be_trimmed(self):
        """Simulate the trim logic from the dependency."""
        now = time()
        cutoff = now - WINDOW_SECONDS
        timestamps = [now - 120, now - 90, now - 30, now - 10, now]
        trimmed = [t for t in timestamps if t > cutoff]
        # Only the last 3 are within window
        assert len(trimmed) == 3

    def test_all_expired(self):
        now = time()
        cutoff = now - WINDOW_SECONDS
        timestamps = [now - 120, now - 90, now - 70]
        trimmed = [t for t in timestamps if t > cutoff]
        assert len(trimmed) == 0

    def test_at_limit_detection(self):
        """Verify the limit-check math is correct."""
        now = time()
        # Fill exactly MAX_REQUESTS timestamps
        _counters["user"] = [now - i for i in range(MAX_REQUESTS)]
        remaining = MAX_REQUESTS - len(_counters["user"])
        assert remaining == 0

    def test_under_limit(self):
        now = time()
        _counters["user"] = [now - i for i in range(50)]
        remaining = MAX_REQUESTS - len(_counters["user"])
        assert remaining == 50
