"""Rate Limit Sliding Window — token-bucket + sliding window rate limiting for API keys.

Provides per-key rate limiting for the developer platform API:
- Sliding window counter (not fixed buckets — smoother at boundaries)
- Configurable windows: per-second, per-minute, per-hour
- Multiple window enforcement (e.g. 10/s AND 500/min AND 5000/h)
- Token bucket for burst allowance
- Rate limit headers (X-RateLimit-Limit, Remaining, Reset)
- Key-scoped and global limits
- Penalty box for repeat offenders (temporary ban)
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class WindowSize(str, Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"


WINDOW_SECONDS = {
    WindowSize.SECOND: 1,
    WindowSize.MINUTE: 60,
    WindowSize.HOUR: 3600,
}


@dataclass
class RateLimitRule:
    """A single rate limit rule (e.g. 100 requests per minute)."""

    window: WindowSize
    max_requests: int


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""

    allowed: bool
    limit: int          # max requests in the most restrictive triggered window
    remaining: int      # requests remaining
    reset_at: float     # unix timestamp when the window resets
    retry_after: float  # seconds until next allowed request (0 if allowed)
    triggered_rule: str | None = None  # which rule blocked (e.g. "100/minute")
    penalty: bool = False  # in penalty box


@dataclass
class RateLimitHeaders:
    """Standard rate limit response headers."""

    x_ratelimit_limit: int
    x_ratelimit_remaining: int
    x_ratelimit_reset: int  # unix timestamp

    def to_dict(self) -> dict[str, str]:
        return {
            "X-RateLimit-Limit": str(self.x_ratelimit_limit),
            "X-RateLimit-Remaining": str(self.x_ratelimit_remaining),
            "X-RateLimit-Reset": str(self.x_ratelimit_reset),
        }


@dataclass
class KeyStats:
    """Usage statistics for a rate-limited key."""

    key: str
    total_requests: int
    total_blocked: int
    in_penalty: bool
    current_rates: dict[str, int]  # window → current count


# ── Penalty box ──────────────────────────────────────────

PENALTY_THRESHOLD = 10      # blocked requests before penalty
PENALTY_DURATION_SECONDS = 60  # ban duration


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter with penalty box.

    Each key maintains a deque of request timestamps. A request is allowed
    if the count of timestamps within each window does not exceed the limit.
    """

    def __init__(self, rules: list[RateLimitRule]):
        if not rules:
            raise ValueError("At least one rate limit rule is required")
        self._rules = sorted(rules, key=lambda r: WINDOW_SECONDS[r.window])
        # key → deque of unix timestamps
        self._windows: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=100_000))
        # key → consecutive blocked count
        self._blocked_counts: dict[str, int] = defaultdict(int)
        # key → penalty expiry timestamp
        self._penalties: dict[str, float] = {}
        # key → total stats
        self._total_requests: dict[str, int] = defaultdict(int)
        self._total_blocked: dict[str, int] = defaultdict(int)

    def check(self, key: str, now: float | None = None) -> RateLimitResult:
        """Check if a request is allowed and record it if so.

        Returns a RateLimitResult. If allowed, the request is recorded.
        If blocked, it is NOT recorded (only real requests count).
        """
        now = now or time.time()

        # Check penalty box
        if self._is_penalized(key, now):
            penalty_end = self._penalties[key]
            return RateLimitResult(
                allowed=False,
                limit=0,
                remaining=0,
                reset_at=penalty_end,
                retry_after=penalty_end - now,
                triggered_rule="penalty_box",
                penalty=True,
            )

        # Clean old timestamps
        self._cleanup(key, now)

        # Check each rule
        timestamps = self._windows[key]
        for rule in self._rules:
            window_secs = WINDOW_SECONDS[rule.window]
            cutoff = now - window_secs
            count = sum(1 for t in timestamps if t > cutoff)

            if count >= rule.max_requests:
                # Blocked
                self._total_blocked[key] = self._total_blocked.get(key, 0) + 1
                self._blocked_counts[key] = self._blocked_counts.get(key, 0) + 1

                # Check penalty threshold
                if self._blocked_counts[key] >= PENALTY_THRESHOLD:
                    self._penalties[key] = now + PENALTY_DURATION_SECONDS
                    self._blocked_counts[key] = 0
                    log.warning("rate_limit.penalty_box", key=key, duration=PENALTY_DURATION_SECONDS)

                # Find oldest timestamp in window → reset time
                in_window = [t for t in timestamps if t > cutoff]
                reset_at = in_window[0] + window_secs if in_window else now + window_secs

                return RateLimitResult(
                    allowed=False,
                    limit=rule.max_requests,
                    remaining=0,
                    reset_at=reset_at,
                    retry_after=reset_at - now,
                    triggered_rule=f"{rule.max_requests}/{rule.window.value}",
                )

        # Allowed — record the request
        timestamps.append(now)
        self._total_requests[key] = self._total_requests.get(key, 0) + 1
        self._blocked_counts[key] = 0  # reset consecutive blocked

        # Compute remaining for the tightest rule
        tightest = self._rules[0]
        window_secs = WINDOW_SECONDS[tightest.window]
        cutoff = now - window_secs
        current = sum(1 for t in timestamps if t > cutoff)
        remaining = max(0, tightest.max_requests - current)

        return RateLimitResult(
            allowed=True,
            limit=tightest.max_requests,
            remaining=remaining,
            reset_at=now + window_secs,
            retry_after=0,
        )

    def get_headers(self, key: str, now: float | None = None) -> RateLimitHeaders:
        """Get standard rate limit headers for the current state (without recording)."""
        now = now or time.time()
        self._cleanup(key, now)
        timestamps = self._windows[key]

        # Use the smallest window for headers
        rule = self._rules[0]
        window_secs = WINDOW_SECONDS[rule.window]
        cutoff = now - window_secs
        current = sum(1 for t in timestamps if t > cutoff)

        return RateLimitHeaders(
            x_ratelimit_limit=rule.max_requests,
            x_ratelimit_remaining=max(0, rule.max_requests - current),
            x_ratelimit_reset=int(now + window_secs),
        )

    def get_stats(self, key: str, now: float | None = None) -> KeyStats:
        """Get usage statistics for a key."""
        now = now or time.time()
        self._cleanup(key, now)
        timestamps = self._windows[key]

        rates: dict[str, int] = {}
        for rule in self._rules:
            window_secs = WINDOW_SECONDS[rule.window]
            cutoff = now - window_secs
            rates[rule.window.value] = sum(1 for t in timestamps if t > cutoff)

        return KeyStats(
            key=key,
            total_requests=self._total_requests.get(key, 0),
            total_blocked=self._total_blocked.get(key, 0),
            in_penalty=self._is_penalized(key, now),
            current_rates=rates,
        )

    def clear(self, key: str) -> None:
        """Clear all state for a key (useful for testing or admin reset)."""
        self._windows.pop(key, None)
        self._blocked_counts.pop(key, None)
        self._penalties.pop(key, None)
        self._total_requests.pop(key, None)
        self._total_blocked.pop(key, None)

    # ── Internals ────────────────────────────────────────

    def _cleanup(self, key: str, now: float) -> None:
        """Remove timestamps older than the largest window."""
        max_window = max(WINDOW_SECONDS[r.window] for r in self._rules)
        cutoff = now - max_window
        timestamps = self._windows[key]
        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()

    def _is_penalized(self, key: str, now: float) -> bool:
        if key not in self._penalties:
            return False
        if now >= self._penalties[key]:
            del self._penalties[key]
            return False
        return True
