"""Tests for Rate Limit Sliding Window — per-key limits, multiple windows, penalty box."""

import pytest

from app.services.rate_limit_window import (
    PENALTY_DURATION_SECONDS,
    PENALTY_THRESHOLD,
    RateLimitRule,
    SlidingWindowRateLimiter,
    WindowSize,
)


class TestBasicLimiting:
    def test_first_request_allowed(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 10)])
        result = rl.check("key-1", now=1000.0)
        assert result.allowed is True
        assert result.remaining == 9

    def test_under_limit_allowed(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 5)])
        for i in range(5):
            result = rl.check("key-1", now=1000.0 + i * 0.1)
        assert result.allowed is True
        assert result.remaining == 0

    def test_over_limit_blocked(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 3)])
        for i in range(3):
            rl.check("key-1", now=1000.0)
        result = rl.check("key-1", now=1000.0)
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after > 0
        assert result.triggered_rule == "3/second"

    def test_window_slides(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 3)])
        for i in range(3):
            rl.check("key-1", now=1000.0)
        # Blocked at 1000.0
        assert rl.check("key-1", now=1000.0).allowed is False
        # Allowed after window slides
        result = rl.check("key-1", now=1001.1)
        assert result.allowed is True

    def test_keys_independent(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 2)])
        rl.check("key-1", now=1000.0)
        rl.check("key-1", now=1000.0)
        assert rl.check("key-1", now=1000.0).allowed is False
        # key-2 still has budget
        assert rl.check("key-2", now=1000.0).allowed is True


class TestMultipleWindows:
    def test_minute_and_hour_rules(self):
        rl = SlidingWindowRateLimiter([
            RateLimitRule(WindowSize.MINUTE, 10),
            RateLimitRule(WindowSize.HOUR, 50),
        ])
        # Use 10 requests in one minute
        for i in range(10):
            rl.check("key-1", now=1000.0 + i)
        # Blocked by minute rule
        result = rl.check("key-1", now=1009.0)
        assert result.allowed is False
        assert "minute" in (result.triggered_rule or "")

    def test_hour_limit_hit_before_minute(self):
        rl = SlidingWindowRateLimiter([
            RateLimitRule(WindowSize.MINUTE, 20),
            RateLimitRule(WindowSize.HOUR, 5),
        ])
        for i in range(5):
            rl.check("key-1", now=1000.0 + i * 60)  # spread over minutes
        result = rl.check("key-1", now=1000.0 + 300)
        assert result.allowed is False
        assert "hour" in (result.triggered_rule or "")


class TestPenaltyBox:
    def test_penalty_after_threshold_blocks(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 1)])
        now = 1000.0
        # First request OK
        rl.check("key-1", now=now)
        # Rack up PENALTY_THRESHOLD blocks (the 10th triggers penalty internally)
        for i in range(PENALTY_THRESHOLD):
            rl.check("key-1", now=now)
        # Next request sees the penalty box
        result = rl.check("key-1", now=now)
        assert result.allowed is False
        assert result.penalty is True
        assert result.triggered_rule == "penalty_box"

    def test_penalty_expires(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 1)])
        now = 1000.0
        rl.check("key-1", now=now)
        for _ in range(PENALTY_THRESHOLD):
            rl.check("key-1", now=now)
        # Still penalized
        result = rl.check("key-1", now=now + 30)
        assert result.penalty is True
        # Penalty expired
        result = rl.check("key-1", now=now + PENALTY_DURATION_SECONDS + 1)
        assert result.penalty is False
        assert result.allowed is True

    def test_penalty_retry_after(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 1)])
        now = 1000.0
        rl.check("key-1", now=now)
        for _ in range(PENALTY_THRESHOLD):
            rl.check("key-1", now=now)
        result = rl.check("key-1", now=now + 10)
        assert result.retry_after == pytest.approx(PENALTY_DURATION_SECONDS - 10, abs=1)


class TestHeaders:
    def test_headers_reflect_state(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.MINUTE, 100)])
        rl.check("key-1", now=1000.0)
        rl.check("key-1", now=1000.0)
        headers = rl.get_headers("key-1", now=1000.0)
        assert headers.x_ratelimit_limit == 100
        assert headers.x_ratelimit_remaining == 98

    def test_headers_to_dict(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.MINUTE, 50)])
        headers = rl.get_headers("key-1", now=1000.0)
        d = headers.to_dict()
        assert "X-RateLimit-Limit" in d
        assert "X-RateLimit-Remaining" in d
        assert "X-RateLimit-Reset" in d
        assert d["X-RateLimit-Limit"] == "50"


class TestStats:
    def test_stats_track_totals(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 3)])
        now = 1000.0
        for _ in range(3):
            rl.check("key-1", now=now)
        rl.check("key-1", now=now)  # blocked
        rl.check("key-1", now=now)  # blocked

        stats = rl.get_stats("key-1", now=now)
        assert stats.total_requests == 3
        assert stats.total_blocked == 2
        assert stats.current_rates["second"] == 3

    def test_stats_empty_key(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.MINUTE, 100)])
        stats = rl.get_stats("unknown-key")
        assert stats.total_requests == 0
        assert stats.total_blocked == 0

    def test_stats_penalty_flag(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 1)])
        now = 1000.0
        rl.check("key-1", now=now)
        for _ in range(PENALTY_THRESHOLD):
            rl.check("key-1", now=now)
        stats = rl.get_stats("key-1", now=now)
        assert stats.in_penalty is True


class TestClear:
    def test_clear_resets_key(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 2)])
        rl.check("key-1", now=1000.0)
        rl.check("key-1", now=1000.0)
        assert rl.check("key-1", now=1000.0).allowed is False
        rl.clear("key-1")
        assert rl.check("key-1", now=1000.0).allowed is True

    def test_clear_nonexistent_no_error(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 10)])
        rl.clear("nonexistent")  # should not raise


class TestEdgeCases:
    def test_no_rules_raises(self):
        with pytest.raises(ValueError, match="At least one"):
            SlidingWindowRateLimiter([])

    def test_blocked_requests_not_counted(self):
        rl = SlidingWindowRateLimiter([RateLimitRule(WindowSize.SECOND, 2)])
        rl.check("key-1", now=1000.0)
        rl.check("key-1", now=1000.0)
        # These are blocked → should not inflate the counter
        rl.check("key-1", now=1000.0)
        rl.check("key-1", now=1000.0)
        # After window slides, should get full budget again
        result = rl.check("key-1", now=1001.1)
        assert result.allowed is True
        assert result.remaining == 1  # used 1 of 2
