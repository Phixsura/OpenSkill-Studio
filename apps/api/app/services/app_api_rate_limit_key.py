"""App API Rate Limit Key — custom rate limit key strategies."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitKey:
    key_id: str
    strategy: str  # "ip", "api_key", "user", "endpoint", "custom"
    identifier: str
    current_count: int = 0
    limit: int = 100
    window_seconds: int = 60

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.current_count)

    @property
    def exhausted(self) -> bool:
        return self.current_count >= self.limit

VALID_STRATEGIES = {"ip", "api_key", "user", "endpoint", "custom"}

class AppAPIRateLimitKey:
    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], RateLimitKey] = {}

    def create(self, installation_id: str, key_id: str, strategy: str, identifier: str, limit: int = 100, window_seconds: int = 60) -> RateLimitKey:
        if not installation_id: raise ValueError("installation_id is required")
        if strategy not in VALID_STRATEGIES: raise ValueError(f"strategy must be one of {VALID_STRATEGIES}")
        k = RateLimitKey(key_id=key_id, strategy=strategy, identifier=identifier, limit=limit, window_seconds=window_seconds)
        self._keys[(installation_id, key_id)] = k
        return k

    def increment(self, installation_id: str, key_id: str) -> RateLimitKey:
        k = self._get(installation_id, key_id)
        k.current_count += 1
        return k

    def is_allowed(self, installation_id: str, key_id: str) -> bool:
        return not self._get(installation_id, key_id).exhausted

    def list_keys(self, installation_id: str) -> list[RateLimitKey]:
        return [k for (inst, _), k in self._keys.items() if inst == installation_id]

    def _get(self, installation_id: str, key_id: str) -> RateLimitKey:
        k = self._keys.get((installation_id, key_id))
        if k is None: raise KeyError(f"Key {key_id} not found")
        return k
