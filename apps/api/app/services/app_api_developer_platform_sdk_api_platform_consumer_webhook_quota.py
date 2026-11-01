"""App API Developer Consumer Webhook Quota — per-consumer webhook delivery quotas."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class WebhookQuota:
    consumer_id: str
    daily_limit: int
    used_today: int = 0
    overage_count: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.daily_limit - self.used_today)

    @property
    def usage_pct(self) -> float:
        return round(self.used_today / self.daily_limit * 100, 1) if self.daily_limit > 0 else 0.0

    @property
    def exhausted(self) -> bool:
        return self.used_today >= self.daily_limit

class AppAPIDeveloperPlatformSDKApiPlatformConsumerWebhookQuota:
    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str], WebhookQuota] = {}

    def set_quota(self, installation_id: str, consumer_id: str, daily_limit: int) -> WebhookQuota:
        if not installation_id: raise ValueError("installation_id is required")
        if daily_limit < 1: raise ValueError("daily_limit must be >= 1")
        key = (installation_id, consumer_id)
        q = WebhookQuota(consumer_id=consumer_id, daily_limit=daily_limit)
        self._quotas[key] = q
        return q

    def consume(self, installation_id: str, consumer_id: str, count: int = 1) -> WebhookQuota:
        key = (installation_id, consumer_id)
        q = self._quotas.get(key)
        if q is None: raise KeyError(f"No quota for {consumer_id}")
        q.used_today += count
        if q.used_today > q.daily_limit: q.overage_count += count
        return q

    def exhausted_consumers(self, installation_id: str) -> list[WebhookQuota]:
        return [q for (inst, _), q in self._quotas.items() if inst == installation_id and q.exhausted]

    def reset_daily(self, installation_id: str) -> int:
        count = 0
        for (inst, _), q in self._quotas.items():
            if inst == installation_id:
                q.used_today = 0
                count += 1
        return count

    def all_quotas(self, installation_id: str) -> list[WebhookQuota]:
        return [q for (inst, _), q in self._quotas.items() if inst == installation_id]
