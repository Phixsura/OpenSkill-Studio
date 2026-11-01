"""Endpoint Rate Limit Policy — tiered rate limits with sliding window."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from collections import deque

logger = structlog.get_logger()


@dataclass
class RateLimitPolicy:
    policy_id: str
    endpoint_id: str
    window_seconds: float
    max_requests: int
    burst_limit: int = 0


@dataclass
class SlidingWindow:
    timestamps: deque = field(default_factory=deque)
    burst_used: int = 0


@dataclass
class RateLimitPolicyManager:
    """Manage per-endpoint rate limits with sliding window algorithm."""

    _policies: dict[str, RateLimitPolicy] = field(default_factory=dict)  # endpoint_id -> policy
    _windows: dict[str, dict[str, SlidingWindow]] = field(default_factory=dict)  # endpoint -> {consumer -> window}
    _total_allowed: int = 0
    _total_denied: int = 0

    def set_policy(self, policy: RateLimitPolicy) -> dict:
        if policy.max_requests < 1:
            raise ValueError("max_requests must be positive")
        if policy.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self._policies[policy.endpoint_id] = policy
        logger.info("rate_limit_policy_set", endpoint_id=policy.endpoint_id)
        return {"endpoint_id": policy.endpoint_id, "max_requests": policy.max_requests,
                "window_seconds": policy.window_seconds}

    def check(self, endpoint_id: str, consumer_id: str, current_time: float) -> dict:
        policy = self._policies.get(endpoint_id)
        if not policy:
            self._total_allowed += 1
            return {"allowed": True, "reason": "no_policy"}

        windows = self._windows.setdefault(endpoint_id, {})
        window = windows.setdefault(consumer_id, SlidingWindow())

        # Clean expired timestamps
        cutoff = current_time - policy.window_seconds
        while window.timestamps and window.timestamps[0] < cutoff:
            window.timestamps.popleft()

        current_count = len(window.timestamps)

        if current_count < policy.max_requests:
            window.timestamps.append(current_time)
            self._total_allowed += 1
            remaining = policy.max_requests - current_count - 1
            return {"allowed": True, "remaining": remaining,
                    "limit": policy.max_requests, "window": policy.window_seconds}

        # Check burst
        if policy.burst_limit > 0 and window.burst_used < policy.burst_limit:
            window.burst_used += 1
            window.timestamps.append(current_time)
            self._total_allowed += 1
            return {"allowed": True, "burst": True,
                    "burst_remaining": policy.burst_limit - window.burst_used}

        self._total_denied += 1
        retry_after = window.timestamps[0] + policy.window_seconds - current_time
        return {"allowed": False, "reason": "rate_limited",
                "retry_after_seconds": round(max(0, retry_after), 2)}

    def reset_burst(self, endpoint_id: str, consumer_id: str) -> dict:
        windows = self._windows.get(endpoint_id, {})
        window = windows.get(consumer_id)
        if window:
            window.burst_used = 0
            return {"reset": True}
        return {"reset": False}

    def get_consumer_usage(self, endpoint_id: str, consumer_id: str,
                           current_time: float) -> dict:
        policy = self._policies.get(endpoint_id)
        if not policy:
            return {"status": "no_policy"}
        windows = self._windows.get(endpoint_id, {})
        window = windows.get(consumer_id)
        if not window:
            return {"current": 0, "limit": policy.max_requests, "usage_pct": 0}
        cutoff = current_time - policy.window_seconds
        current = sum(1 for t in window.timestamps if t >= cutoff)
        return {
            "current": current,
            "limit": policy.max_requests,
            "usage_pct": round(current / policy.max_requests * 100, 1),
            "burst_used": window.burst_used,
            "burst_limit": policy.burst_limit,
        }

    def list_policies(self) -> list[dict]:
        return [
            {"endpoint_id": p.endpoint_id, "max_requests": p.max_requests,
             "window_seconds": p.window_seconds, "burst_limit": p.burst_limit}
            for p in self._policies.values()
        ]

    def get_stats(self) -> dict:
        return {
            "total_policies": len(self._policies),
            "total_allowed": self._total_allowed,
            "total_denied": self._total_denied,
            "deny_rate": round(self._total_denied / (self._total_allowed + self._total_denied) * 100, 2)
            if (self._total_allowed + self._total_denied) > 0 else 0,
        }
