"""Consumer Quota Rollover — carry unused quota to the next billing period."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class QuotaPeriod:
    period_id: str
    consumer_id: str
    base_quota: int
    used: int = 0
    rolled_in: int = 0   # carried from previous period
    rolled_out: int = 0  # carried to next period

    @property
    def total_available(self) -> int:
        return self.base_quota + self.rolled_in

    @property
    def remaining(self) -> int:
        return max(0, self.total_available - self.used)

@dataclass
class RolloverPolicy:
    max_rollover_pct: float = 0.2   # max 20% of base can roll over
    max_accumulation: int = 3       # max periods of accumulation

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerQuotaRollover:
    def __init__(self) -> None:
        self._periods: dict[tuple[str, str, str], QuotaPeriod] = {}  # (inst, consumer, period)
        self._policies: dict[tuple[str, str], RolloverPolicy] = {}

    def set_policy(self, installation_id: str, consumer_id: str, policy: RolloverPolicy) -> RolloverPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (0.0 <= policy.max_rollover_pct <= 1.0):
            raise ValueError("max_rollover_pct must be between 0 and 1")
        self._policies[(installation_id, consumer_id)] = policy
        return policy

    def create_period(self, installation_id: str, consumer_id: str, period: QuotaPeriod) -> QuotaPeriod:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, period.period_id)
        self._periods[key] = period
        return period

    def use_quota(self, installation_id: str, consumer_id: str, period_id: str, amount: int) -> QuotaPeriod:
        key = (installation_id, consumer_id, period_id)
        period = self._periods.get(key)
        if not period:
            raise ValueError(f"Period {period_id} not found")
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        period.used += amount
        return period

    def rollover(self, installation_id: str, consumer_id: str, from_period_id: str, to_period_id: str) -> int:
        from_key = (installation_id, consumer_id, from_period_id)
        to_key = (installation_id, consumer_id, to_period_id)
        from_p = self._periods.get(from_key)
        to_p = self._periods.get(to_key)
        if not from_p or not to_p:
            raise ValueError("Both periods must exist")
        policy = self._policies.get((installation_id, consumer_id), RolloverPolicy())
        max_roll = int(from_p.base_quota * policy.max_rollover_pct)
        actual = min(from_p.remaining, max_roll)
        from_p.rolled_out = actual
        to_p.rolled_in = actual
        log.info("quota_rollover", installation_id=installation_id, consumer_id=consumer_id, amount=actual)
        return actual

    def get_period(self, installation_id: str, consumer_id: str, period_id: str) -> QuotaPeriod | None:
        return self._periods.get((installation_id, consumer_id, period_id))
