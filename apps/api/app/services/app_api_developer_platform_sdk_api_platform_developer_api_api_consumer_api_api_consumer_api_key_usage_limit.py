"""API Consumer API Key Usage Limit — enforce per-key usage limits."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class KeyUsageLimit:
    key_id: str
    consumer_id: str
    daily_limit: int
    monthly_limit: int
    daily_used: int = 0
    monthly_used: int = 0

    @property
    def daily_remaining(self) -> int:
        return max(0, self.daily_limit - self.daily_used)

    @property
    def monthly_remaining(self) -> int:
        return max(0, self.monthly_limit - self.monthly_used)

    @property
    def daily_exhausted(self) -> bool:
        return self.daily_used >= self.daily_limit

    @property
    def monthly_exhausted(self) -> bool:
        return self.monthly_used >= self.monthly_limit

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyUsageLimit:
    def __init__(self) -> None:
        self._limits: dict[tuple[str, str], KeyUsageLimit] = {}

    def set_limit(self, installation_id: str, limit: KeyUsageLimit) -> KeyUsageLimit:
        if not installation_id: raise ValueError("installation_id is required")
        if limit.daily_limit < 1: raise ValueError("daily_limit must be >= 1")
        if limit.monthly_limit < limit.daily_limit: raise ValueError("monthly must be >= daily")
        self._limits[(installation_id, limit.key_id)] = limit
        return limit

    def consume(self, installation_id: str, key_id: str, count: int = 1) -> KeyUsageLimit:
        key = (installation_id, key_id)
        l = self._limits.get(key)
        if l is None: raise KeyError(f"No limit for {key_id}")
        if count < 1: raise ValueError("count must be >= 1")
        if l.daily_used + count > l.daily_limit: raise ValueError("Daily limit exceeded")
        if l.monthly_used + count > l.monthly_limit: raise ValueError("Monthly limit exceeded")
        l.daily_used += count
        l.monthly_used += count
        return l

    def reset_daily(self, installation_id: str, key_id: str) -> KeyUsageLimit:
        l = self._limits.get((installation_id, key_id))
        if l is None: raise KeyError(f"No limit for {key_id}")
        l.daily_used = 0
        return l

    def near_limit(self, installation_id: str, threshold_pct: float = 80.0) -> list[KeyUsageLimit]:
        result = []
        for (inst, _), l in self._limits.items():
            if inst != installation_id: continue
            daily_pct = (l.daily_used / l.daily_limit * 100) if l.daily_limit > 0 else 0
            monthly_pct = (l.monthly_used / l.monthly_limit * 100) if l.monthly_limit > 0 else 0
            if daily_pct >= threshold_pct or monthly_pct >= threshold_pct:
                result.append(l)
        return result

    def list_limits(self, installation_id: str) -> list[KeyUsageLimit]:
        return [l for (inst, _), l in self._limits.items() if inst == installation_id]
