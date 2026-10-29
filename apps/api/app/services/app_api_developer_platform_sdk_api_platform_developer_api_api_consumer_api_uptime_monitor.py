"""API Consumer Uptime Monitor — track API uptime with SLA reporting."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class UptimeRecord:
    period: str  # "2024-01-15"
    total_checks: int = 0
    successful_checks: int = 0
    downtime_minutes: float = 0.0

    @property
    def uptime_pct(self) -> float:
        if self.total_checks == 0: return 100.0
        return round((self.successful_checks / self.total_checks) * 100, 3)

@dataclass
class UptimeSummary:
    endpoint: str
    records: list[UptimeRecord] = field(default_factory=list)

    @property
    def overall_uptime(self) -> float:
        total = sum(r.total_checks for r in self.records)
        success = sum(r.successful_checks for r in self.records)
        if total == 0: return 100.0
        return round((success / total) * 100, 3)

    @property
    def total_downtime_minutes(self) -> float:
        return round(sum(r.downtime_minutes for r in self.records), 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUptimeMonitor:
    def __init__(self) -> None:
        self._summaries: dict[tuple[str, str], UptimeSummary] = {}

    def record_check(self, installation_id: str, endpoint: str, period: str, success: bool, downtime_min: float = 0.0) -> UptimeRecord:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        summary = self._summaries.get(key)
        if summary is None:
            summary = UptimeSummary(endpoint=endpoint)
            self._summaries[key] = summary
        record = next((r for r in summary.records if r.period == period), None)
        if record is None:
            record = UptimeRecord(period=period)
            summary.records.append(record)
        record.total_checks += 1
        if success: record.successful_checks += 1
        else: record.downtime_minutes += downtime_min
        return record

    def get_uptime(self, installation_id: str, endpoint: str) -> float:
        summary = self._summaries.get((installation_id, endpoint))
        if summary is None: return 100.0
        return summary.overall_uptime

    def sla_breaches(self, installation_id: str, sla_target: float = 99.9) -> list[tuple[str, float]]:
        breaches = []
        for (inst, ep), s in self._summaries.items():
            if inst == installation_id and s.overall_uptime < sla_target:
                breaches.append((ep, s.overall_uptime))
        return breaches

    def list_endpoints(self, installation_id: str) -> list[UptimeSummary]:
        return [s for (inst, _), s in self._summaries.items() if inst == installation_id]
