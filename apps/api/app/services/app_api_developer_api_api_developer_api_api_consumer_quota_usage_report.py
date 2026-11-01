"""App API Developer Consumer Quota Usage Report — periodic quota consumption reports."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class QuotaUsageEntry:
    consumer_id: str
    period: str  # "2025-01", "2025-01-15"
    api_calls_used: int = 0
    api_calls_limit: int = 0
    webhooks_used: int = 0
    webhooks_limit: int = 0
    storage_used_mb: float = 0.0
    storage_limit_mb: float = 0.0

    @property
    def api_usage_pct(self) -> float:
        return round(self.api_calls_used / self.api_calls_limit * 100, 1) if self.api_calls_limit > 0 else 0.0

    @property
    def any_over_limit(self) -> bool:
        return (self.api_calls_used > self.api_calls_limit or
                self.webhooks_used > self.webhooks_limit or
                self.storage_used_mb > self.storage_limit_mb)

class AppAPIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str, str], QuotaUsageEntry] = {}

    def record(self, installation_id: str, consumer_id: str, period: str, **kwargs) -> QuotaUsageEntry:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, period)
        e = QuotaUsageEntry(consumer_id=consumer_id, period=period)
        for k, v in kwargs.items():
            if hasattr(e, k): setattr(e, k, v)
        self._reports[key] = e
        return e

    def get(self, installation_id: str, consumer_id: str, period: str) -> QuotaUsageEntry | None:
        return self._reports.get((installation_id, consumer_id, period))

    def over_limit(self, installation_id: str, period: str) -> list[QuotaUsageEntry]:
        return [e for (inst, _, p), e in self._reports.items() if inst == installation_id and p == period and e.any_over_limit]

    def by_consumer(self, installation_id: str, consumer_id: str) -> list[QuotaUsageEntry]:
        return [e for (inst, cid, _), e in self._reports.items() if inst == installation_id and cid == consumer_id]

    def all_reports(self, installation_id: str, period: str) -> list[QuotaUsageEntry]:
        return [e for (inst, _, p), e in self._reports.items() if inst == installation_id and p == period]
