"""Sandbox API Rate Window — sliding window rate limiter for sandbox APIs.

Implements precise sliding window rate limiting with per-second/minute/hour
granularity, burst allowance, and rate limit header generation.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RateWindow:
    window_seconds: int
    max_requests: int
    burst: int = 0  # extra burst above limit


@dataclass
class RateState:
    timestamps: list[float] = field(default_factory=list)
    burst_used: int = 0


class SandboxApiRateWindowService:
    """Sliding window rate limiter with burst and headers."""

    def __init__(self):
        self._windows: dict[str, dict[str, RateWindow]] = defaultdict(dict)
        self._state: dict[str, dict[str, RateState]] = defaultdict(lambda: defaultdict(RateState))

    def configure(self, sandbox_id: str, endpoint: str,
                  window_seconds: int, max_requests: int,
                  burst: int = 0) -> RateWindow:
        window = RateWindow(window_seconds=window_seconds,
                            max_requests=max_requests, burst=burst)
        self._windows[sandbox_id][endpoint] = window
        return window

    def check(self, sandbox_id: str, endpoint: str) -> dict:
        window = self._windows.get(sandbox_id, {}).get(endpoint)
        if not window:
            return {"allowed": True, "remaining": 999, "limit": 999}

        now = time.time()
        state = self._state[sandbox_id][endpoint]
        cutoff = now - window.window_seconds

        # Remove expired timestamps
        state.timestamps = [ts for ts in state.timestamps if ts > cutoff]
        count = len(state.timestamps)
        total_limit = window.max_requests + window.burst

        if count >= total_limit:
            oldest = state.timestamps[0] if state.timestamps else now
            retry_after = round(oldest + window.window_seconds - now, 1)
            return {
                "allowed": False,
                "remaining": 0,
                "limit": window.max_requests,
                "retry_after": max(0, retry_after),
                "headers": {
                    "X-RateLimit-Limit": str(window.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(int(max(0, retry_after))),
                },
            }

        state.timestamps.append(now)
        remaining = max(0, window.max_requests - len(state.timestamps))
        used_burst = max(0, len(state.timestamps) - window.max_requests)

        return {
            "allowed": True,
            "remaining": remaining,
            "limit": window.max_requests,
            "used_burst": used_burst,
            "headers": {
                "X-RateLimit-Limit": str(window.max_requests),
                "X-RateLimit-Remaining": str(remaining),
            },
        }

    def get_usage(self, sandbox_id: str, endpoint: str) -> dict:
        window = self._windows.get(sandbox_id, {}).get(endpoint)
        if not window:
            return {"configured": False}
        state = self._state[sandbox_id][endpoint]
        now = time.time()
        cutoff = now - window.window_seconds
        active = [ts for ts in state.timestamps if ts > cutoff]
        return {
            "configured": True,
            "current": len(active),
            "limit": window.max_requests,
            "burst": window.burst,
            "window_seconds": window.window_seconds,
            "usage_percent": round(len(active) / max(window.max_requests, 1) * 100, 1),
        }

    def reset(self, sandbox_id: str, endpoint: str) -> bool:
        if endpoint in self._state.get(sandbox_id, {}):
            self._state[sandbox_id][endpoint] = RateState()
            return True
        return False

    def list_endpoints(self, sandbox_id: str) -> list[str]:
        return sorted(self._windows.get(sandbox_id, {}).keys())
