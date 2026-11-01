"""Rate Limit Policy — configurable per-endpoint rate limiting for extensions.

Supports sliding window and token bucket algorithms, per-user and per-IP
limits, custom policies per endpoint, and rate limit header generation.
"""
from __future__ import annotations
import time
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class Algorithm(str, Enum):
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


@dataclass
class RateLimitPolicy:
    policy_id: str
    extension_id: str
    endpoint: str
    algorithm: Algorithm
    max_requests: int
    window_seconds: int
    burst_size: int = 0  # token bucket burst


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    limit: int
    reset_at: float
    retry_after: float = 0.0

    @property
    def headers(self) -> dict[str, str]:
        return {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(0, self.remaining)),
            "X-RateLimit-Reset": str(int(self.reset_at)),
            **({"Retry-After": str(int(self.retry_after))} if not self.allowed else {}),
        }


class RateLimitPolicyService:
    """Enforces per-endpoint rate limits with multiple algorithms."""

    def __init__(self):
        self._policies: dict[str, RateLimitPolicy] = {}
        self._policy_by_endpoint: dict[str, dict[str, str]] = defaultdict(dict)
        # Sliding window: {policy_id+key: [timestamps]}
        self._windows: dict[str, list[float]] = defaultdict(list)
        # Token bucket: {policy_id+key: (tokens, last_refill)}
        self._buckets: dict[str, tuple[float, float]] = {}

    def create_policy(self, extension_id: str, endpoint: str,
                      algorithm: Algorithm, max_requests: int,
                      window_seconds: int, burst_size: int = 0) -> RateLimitPolicy:
        if max_requests < 1:
            raise ValueError("max_requests must be >= 1")
        if window_seconds < 1:
            raise ValueError("window_seconds must be >= 1")

        policy_id = f"rlp_{secrets.token_urlsafe(8)}"
        policy = RateLimitPolicy(
            policy_id=policy_id, extension_id=extension_id,
            endpoint=endpoint, algorithm=algorithm,
            max_requests=max_requests, window_seconds=window_seconds,
            burst_size=burst_size or max_requests,
        )
        self._policies[policy_id] = policy
        self._policy_by_endpoint[extension_id][endpoint] = policy_id
        return policy

    def check(self, extension_id: str, endpoint: str,
              key: str = "default") -> RateLimitResult:
        policy_id = self._policy_by_endpoint.get(extension_id, {}).get(endpoint)
        if not policy_id:
            return RateLimitResult(allowed=True, remaining=999, limit=999,
                                   reset_at=time.time() + 60)

        policy = self._policies[policy_id]
        bucket_key = f"{policy_id}:{key}"

        if policy.algorithm == Algorithm.SLIDING_WINDOW:
            return self._check_sliding_window(policy, bucket_key)
        else:
            return self._check_token_bucket(policy, bucket_key)

    def _check_sliding_window(self, policy: RateLimitPolicy,
                               bucket_key: str) -> RateLimitResult:
        now = time.time()
        window_start = now - policy.window_seconds
        # Remove old entries
        self._windows[bucket_key] = [
            ts for ts in self._windows[bucket_key] if ts > window_start
        ]
        count = len(self._windows[bucket_key])
        reset_at = now + policy.window_seconds

        if count >= policy.max_requests:
            oldest = self._windows[bucket_key][0] if self._windows[bucket_key] else now
            retry_after = oldest + policy.window_seconds - now
            return RateLimitResult(
                allowed=False, remaining=0, limit=policy.max_requests,
                reset_at=reset_at, retry_after=max(0, retry_after),
            )

        self._windows[bucket_key].append(now)
        return RateLimitResult(
            allowed=True, remaining=policy.max_requests - count - 1,
            limit=policy.max_requests, reset_at=reset_at,
        )

    def _check_token_bucket(self, policy: RateLimitPolicy,
                             bucket_key: str) -> RateLimitResult:
        now = time.time()
        if bucket_key not in self._buckets:
            self._buckets[bucket_key] = (float(policy.burst_size), now)

        tokens, last_refill = self._buckets[bucket_key]
        elapsed = now - last_refill
        refill_rate = policy.max_requests / policy.window_seconds
        tokens = min(policy.burst_size, tokens + elapsed * refill_rate)

        if tokens >= 1:
            tokens -= 1
            self._buckets[bucket_key] = (tokens, now)
            return RateLimitResult(
                allowed=True, remaining=int(tokens),
                limit=policy.max_requests,
                reset_at=now + policy.window_seconds,
            )

        wait = (1 - tokens) / refill_rate
        self._buckets[bucket_key] = (tokens, now)
        return RateLimitResult(
            allowed=False, remaining=0, limit=policy.max_requests,
            reset_at=now + wait, retry_after=wait,
        )

    def get_policies(self, extension_id: str) -> list[RateLimitPolicy]:
        policy_ids = self._policy_by_endpoint.get(extension_id, {}).values()
        return [self._policies[pid] for pid in policy_ids]
