"""App API Developer API Usage Summary — per-developer usage overview."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeveloperUsageSummary:
    developer_id: str
    total_requests: int = 0
    unique_endpoints: int = 0
    avg_latency_ms: float = 0.0
    error_count: int = 0
    webhook_deliveries: int = 0
    api_keys_active: int = 0

    @property
    def error_rate_pct(self) -> float:
        return round(self.error_count / self.total_requests * 100, 2) if self.total_requests > 0 else 0.0

    @property
    def activity_level(self) -> str:
        if self.total_requests >= 10000: return "power"
        if self.total_requests >= 1000: return "active"
        if self.total_requests >= 100: return "moderate"
        if self.total_requests > 0: return "light"
        return "inactive"

class AppAPIDeveloperAPIApiDeveloperApiUsageSummary:
    def __init__(self) -> None:
        self._summaries: dict[tuple[str, str], DeveloperUsageSummary] = {}

    def update(self, installation_id: str, developer_id: str, **kwargs) -> DeveloperUsageSummary:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, developer_id)
        s = DeveloperUsageSummary(developer_id=developer_id)
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._summaries[key] = s
        return s

    def get(self, installation_id: str, developer_id: str) -> DeveloperUsageSummary:
        return self._summaries.get((installation_id, developer_id), DeveloperUsageSummary(developer_id=developer_id))

    def top_developers(self, installation_id: str, limit: int = 10) -> list[DeveloperUsageSummary]:
        devs = [s for (inst, _), s in self._summaries.items() if inst == installation_id]
        return sorted(devs, key=lambda s: s.total_requests, reverse=True)[:limit]

    def by_activity_level(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), s in self._summaries.items():
            if inst == installation_id:
                counts[s.activity_level] = counts.get(s.activity_level, 0) + 1
        return counts
