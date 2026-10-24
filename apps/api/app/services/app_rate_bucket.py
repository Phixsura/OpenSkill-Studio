"""Token bucket rate limiter — per-app token bucket implementation."""

import time
from dataclasses import dataclass, field


@dataclass
class TokenBucket:
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float = 0
    last_refill: float = field(default_factory=time.monotonic)

    def __post_init__(self):
        self.tokens = float(self.capacity)

    def consume(self, tokens: int = 1) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    @property
    def available(self) -> int:
        self._refill()
        return int(self.tokens)


_buckets: dict[str, TokenBucket] = {}

TIER_CONFIGS = {
    "standard": {"capacity": 1000, "refill_rate": 16.7},    # 1000/min
    "premium": {"capacity": 5000, "refill_rate": 83.3},     # 5000/min
    "enterprise": {"capacity": 20000, "refill_rate": 333.3}, # 20000/min
}


def get_bucket(app_id: str, tier: str = "standard") -> TokenBucket:
    key = f"{app_id}:{tier}"
    if key not in _buckets:
        config = TIER_CONFIGS.get(tier, TIER_CONFIGS["standard"])
        _buckets[key] = TokenBucket(**config)
    return _buckets[key]


def try_consume(app_id: str, tier: str = "standard", tokens: int = 1) -> bool:
    return get_bucket(app_id, tier).consume(tokens)
