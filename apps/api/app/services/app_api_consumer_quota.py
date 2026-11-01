"""App API Consumer Quota — per-consumer API quotas with enforcement."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerQuota:
    consumer_id: str
    daily_limit: int
    daily_used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.daily_limit - self.daily_used)

    @property
    def exhausted(self) -> bool:
        return self.daily_used >= self.daily_limit

class AppAPIConsumerQuota:
    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str], ConsumerQuota] = {}

    def set_quota(self, installation_id: str, consumer_id: str, daily_limit: int) -> ConsumerQuota:
        if not installation_id: raise ValueError("installation_id is required")
        if daily_limit < 0: raise ValueError("daily_limit must be non-negative")
        q = ConsumerQuota(consumer_id=consumer_id, daily_limit=daily_limit)
        self._quotas[(installation_id, consumer_id)] = q
        return q

    def consume(self, installation_id: str, consumer_id: str, amount: int = 1) -> ConsumerQuota:
        if amount < 0: raise ValueError("amount must be non-negative")
        q = self._get(installation_id, consumer_id)
        if q.daily_used + amount > q.daily_limit:
            raise ValueError("Quota exhausted")
        q.daily_used += amount
        return q

    def reset_all(self, installation_id: str) -> int:
        count = 0
        for (inst, _), q in self._quotas.items():
            if inst == installation_id:
                q.daily_used = 0
                count += 1
        return count

    def exhausted_consumers(self, installation_id: str) -> list[ConsumerQuota]:
        return [q for (inst, _), q in self._quotas.items() if inst == installation_id and q.exhausted]

    def list_quotas(self, installation_id: str) -> list[ConsumerQuota]:
        return [q for (inst, _), q in self._quotas.items() if inst == installation_id]

    def _get(self, installation_id: str, consumer_id: str) -> ConsumerQuota:
        q = self._quotas.get((installation_id, consumer_id))
        if q is None: raise KeyError(f"Quota for {consumer_id} not found")
        return q
