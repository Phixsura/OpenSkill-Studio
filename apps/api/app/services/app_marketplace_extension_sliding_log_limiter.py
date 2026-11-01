"""Sliding Log Rate Limiter — precise per-request timestamp tracking.

Unlike fixed-window counters, sliding log tracks each request's timestamp
for exact rate calculation. Tradeoff: more memory, but no boundary burst.

Implements:
- Per-key sliding log with configurable window
- Multi-window support (per-second, per-minute, per-hour simultaneously)
- Weighted requests (some endpoints cost more)
- Burst allowance on top of sustained rate
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import time


@dataclass
class RateWindow:
    name: str
    window_seconds: float
    max_requests: int


@dataclass
class SlidingLog:
    key: str
    entries: deque = field(default_factory=lambda: deque(maxlen=50000))
    total_weight: float = 0.0


class SlidingLogLimiterService:
    def __init__(self):
        self._logs: dict[str, SlidingLog] = {}
        self._windows: list[RateWindow] = [
            RateWindow("per_second", 1.0, 10),
            RateWindow("per_minute", 60.0, 300),
            RateWindow("per_hour", 3600.0, 5000),
        ]
        self._burst_allowance: dict[str, float] = {}  # key -> extra burst tokens

    def configure_windows(self, windows: list[tuple[str, float, int]]) -> None:
        self._windows = [RateWindow(n, w, m) for n, w, m in windows]

    def set_burst(self, key: str, extra_tokens: float) -> None:
        self._burst_allowance[key] = extra_tokens

    def check(self, key: str, weight: float = 1.0) -> dict:
        """Check if request is allowed. Returns detailed result."""
        now = time.time()
        log = self._get_log(key)

        # Prune oldest entries beyond largest window
        max_window = max(w.window_seconds for w in self._windows) if self._windows else 3600
        while log.entries and log.entries[0][0] < now - max_window:
            _, w = log.entries.popleft()
            log.total_weight -= w

        # Check each window
        violations = []
        remaining = {}
        for window in self._windows:
            cutoff = now - window.window_seconds
            window_weight = sum(w for ts, w in log.entries if ts >= cutoff)
            burst = self._burst_allowance.get(key, 0)
            effective_limit = window.max_requests + burst

            if window_weight + weight > effective_limit:
                violations.append({
                    "window": window.name,
                    "current": round(window_weight, 1),
                    "limit": effective_limit,
                    "retry_after": self._calc_retry_after(log, window, now, weight),
                })
            remaining[window.name] = max(0, round(effective_limit - window_weight - weight, 1))

        allowed = len(violations) == 0

        if allowed:
            log.entries.append((now, weight))
            log.total_weight += weight

        return {
            "allowed": allowed,
            "remaining": remaining,
            "violations": violations,
            "total_requests": len(log.entries),
        }

    def _calc_retry_after(self, log: SlidingLog, window: RateWindow,
                          now: float, weight: float) -> float:
        """Calculate when enough capacity frees up."""
        cutoff = now - window.window_seconds
        entries_in_window = [(ts, w) for ts, w in log.entries if ts >= cutoff]
        if not entries_in_window:
            return 0
        # Oldest entry in window — when it exits
        oldest_ts = entries_in_window[0][0]
        return round(oldest_ts + window.window_seconds - now + 0.1, 1)

    def _get_log(self, key: str) -> SlidingLog:
        if key not in self._logs:
            self._logs[key] = SlidingLog(key=key)
        return self._logs[key]

    def get_usage(self, key: str) -> dict:
        now = time.time()
        log = self._logs.get(key)
        if not log:
            return {w.name: 0 for w in self._windows}
        result = {}
        for window in self._windows:
            cutoff = now - window.window_seconds
            count = sum(w for ts, w in log.entries if ts >= cutoff)
            result[window.name] = {"used": round(count, 1), "limit": window.max_requests,
                                   "pct": round(count / window.max_requests * 100, 1) if window.max_requests else 0}
        return result
