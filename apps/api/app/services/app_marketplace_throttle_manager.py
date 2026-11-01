"""Throttle Manager — adaptive throttling for extension API endpoints.

Implements sliding window rate limiting with adaptive thresholds
that adjust based on server load and error rates.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ThrottleConfig:
    requests_per_window: int = 100
    window_seconds: float = 60.0
    burst_limit: int = 20  # max requests in 1 second
    adaptive: bool = True
    load_threshold: float = 0.8  # reduce limits above this load


class ThrottleManager:
    """Adaptive sliding-window throttle for extension APIs."""

    def __init__(self, server_load: float = 0.0):
        self._configs: dict[str, ThrottleConfig] = {}
        self._windows: dict[str, list[float]] = defaultdict(list)
        self._server_load = server_load
        self._rejected: dict[str, int] = defaultdict(int)

    def configure(self, key: str, config: ThrottleConfig) -> None:
        self._configs[key] = config

    def set_server_load(self, load: float) -> None:
        self._server_load = min(1.0, max(0.0, load))

    def _effective_limit(self, config: ThrottleConfig) -> int:
        """Calculate effective limit based on server load."""
        if not config.adaptive or self._server_load <= config.load_threshold:
            return config.requests_per_window
        # Scale down linearly above threshold
        scale = 1.0 - (self._server_load - config.load_threshold) / (1.0 - config.load_threshold)
        return max(1, int(config.requests_per_window * scale))

    def _clean_window(self, key: str, window_seconds: float) -> None:
        cutoff = time.monotonic() - window_seconds
        self._windows[key] = [t for t in self._windows[key] if t > cutoff]

    def allow(self, key: str) -> tuple[bool, dict]:
        """Check if request is allowed. Returns (allowed, info)."""
        config = self._configs.get(key, ThrottleConfig())
        now = time.monotonic()

        self._clean_window(key, config.window_seconds)
        timestamps = self._windows[key]

        effective_limit = self._effective_limit(config)
        window_count = len(timestamps)

        # Check burst limit (last 1 second)
        recent = sum(1 for t in timestamps if t > now - 1.0)
        if recent >= config.burst_limit:
            self._rejected[key] += 1
            return False, {"reason": "burst_limit", "retry_after_ms": 1000,
                           "limit": config.burst_limit, "current": recent}

        # Check window limit
        if window_count >= effective_limit:
            self._rejected[key] += 1
            oldest = min(timestamps) if timestamps else now
            retry_after = oldest + config.window_seconds - now
            return False, {"reason": "rate_limit", "retry_after_ms": int(retry_after * 1000),
                           "limit": effective_limit, "current": window_count}

        timestamps.append(now)
        return True, {"remaining": effective_limit - window_count - 1,
                       "limit": effective_limit, "window_seconds": config.window_seconds}

    def get_stats(self, key: str) -> dict:
        config = self._configs.get(key, ThrottleConfig())
        self._clean_window(key, config.window_seconds)
        return {
            "key": key,
            "current_requests": len(self._windows.get(key, [])),
            "effective_limit": self._effective_limit(config),
            "base_limit": config.requests_per_window,
            "server_load": self._server_load,
            "rejected_total": self._rejected.get(key, 0),
        }

    def reset(self, key: str) -> None:
        self._windows.pop(key, None)
        self._rejected.pop(key, None)
