"""Rate Limiter Aggregator — multi-level hierarchical rate limiting.

Unlike single-bucket limiters, this enforces limits at multiple levels
simultaneously: global, per-tenant, per-user, per-endpoint.

Implements:
- Hierarchical limit chains (all levels must pass)
- Per-level token buckets with independent rates
- Burst allowance per level
- Which-level-blocked reporting for debugging
- Dynamic limit adjustment per tenant
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class RateLevel:
    name: str
    key: str  # e.g. "global", "tenant:acme", "user:123", "endpoint:/api/data"
    max_per_second: float
    burst: int
    tokens: float = 0.0
    last_refill: float = 0.0

    def __post_init__(self):
        if self.tokens == 0:
            self.tokens = float(self.burst)
        if not self.last_refill:
            self.last_refill = time.time()


class RateAggregatorService:
    def __init__(self):
        self._levels: dict[str, RateLevel] = {}
        self._chains: dict[str, list[str]] = {}  # chain_name -> [level_keys]
        self._total_allowed = 0
        self._total_denied = 0

    def define_level(self, name: str, key: str, max_per_second: float,
                     burst: int) -> RateLevel:
        level = RateLevel(name=name, key=key, max_per_second=max_per_second,
                          burst=burst)
        self._levels[key] = level
        return level

    def define_chain(self, chain_name: str, level_keys: list[str]) -> None:
        self._chains[chain_name] = level_keys

    def _refill(self, level: RateLevel) -> None:
        now = time.time()
        elapsed = now - level.last_refill
        level.tokens = min(level.burst,
                           level.tokens + elapsed * level.max_per_second)
        level.last_refill = now

    def check(self, chain_name: str, cost: float = 1.0) -> dict:
        """Check all levels in a chain. ALL must pass."""
        keys = self._chains.get(chain_name, [])
        if not keys:
            return {"allowed": True, "reason": "no chain defined"}

        # Pre-check all levels
        blocked_by = None
        for key in keys:
            level = self._levels.get(key)
            if not level:
                continue
            self._refill(level)
            if level.tokens < cost:
                blocked_by = level
                break

        if blocked_by:
            self._total_denied += 1
            wait = (cost - blocked_by.tokens) / blocked_by.max_per_second
            return {
                "allowed": False,
                "blocked_by": blocked_by.name,
                "blocked_key": blocked_by.key,
                "retry_after_ms": round(wait * 1000, 1),
                "remaining": {k: round(self._levels[k].tokens, 1)
                              for k in keys if k in self._levels},
            }

        # All pass — consume
        for key in keys:
            level = self._levels.get(key)
            if level:
                level.tokens -= cost

        self._total_allowed += 1
        return {
            "allowed": True,
            "remaining": {k: round(self._levels[k].tokens, 1)
                          for k in keys if k in self._levels},
        }

    def adjust_limit(self, key: str, max_per_second: float = 0,
                     burst: int = 0) -> bool:
        level = self._levels.get(key)
        if not level:
            return False
        if max_per_second > 0:
            level.max_per_second = max_per_second
        if burst > 0:
            level.burst = burst
        return True

    def get_stats(self) -> dict:
        return {
            "levels": len(self._levels),
            "chains": len(self._chains),
            "total_allowed": self._total_allowed,
            "total_denied": self._total_denied,
            "deny_rate": round(self._total_denied / max(1, self._total_allowed + self._total_denied) * 100, 1),
        }
