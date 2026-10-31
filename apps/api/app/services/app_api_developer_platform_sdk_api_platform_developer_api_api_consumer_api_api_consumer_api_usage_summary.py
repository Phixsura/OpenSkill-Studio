"""API Consumer Usage Summary — comprehensive per-consumer API usage summary."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerUsageSummary:
    consumer_id: str
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    avg_latency_ms: float = 0.0
    unique_endpoints: int = 0
    data_in_bytes: int = 0
    data_out_bytes: int = 0
    active_api_keys: int = 0
    webhook_subscriptions: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return round((self.successful / self.total_requests) * 100, 1)

    @property
    def data_total_mb(self) -> float:
        return round((self.data_in_bytes + self.data_out_bytes) / 1048576, 2)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageSummary:
    def __init__(self) -> None:
        self._summaries: dict[tuple[str, str], ConsumerUsageSummary] = {}

    def update(self, installation_id: str, summary: ConsumerUsageSummary) -> ConsumerUsageSummary:
        if not installation_id: raise ValueError("installation_id is required")
        self._summaries[(installation_id, summary.consumer_id)] = summary
        return summary

    def get_summary(self, installation_id: str, consumer_id: str) -> ConsumerUsageSummary | None:
        return self._summaries.get((installation_id, consumer_id))

    def top_by_requests(self, installation_id: str, limit: int = 10) -> list[ConsumerUsageSummary]:
        summaries = [s for (inst, _), s in self._summaries.items() if inst == installation_id]
        return sorted(summaries, key=lambda s: -s.total_requests)[:limit]

    def low_success_rate(self, installation_id: str, threshold: float = 95.0) -> list[ConsumerUsageSummary]:
        return [s for (inst, _), s in self._summaries.items() if inst == installation_id and s.success_rate < threshold and s.total_requests > 0]

    def list_summaries(self, installation_id: str) -> list[ConsumerUsageSummary]:
        return [s for (inst, _), s in self._summaries.items() if inst == installation_id]
