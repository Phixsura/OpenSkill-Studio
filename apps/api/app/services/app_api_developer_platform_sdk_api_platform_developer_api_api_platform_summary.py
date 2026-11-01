"""API Platform Summary — unified summary of the entire developer platform."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PlatformSummary:
    total_consumers: int = 0
    active_consumers: int = 0
    total_api_keys: int = 0
    total_webhooks: int = 0
    total_requests_24h: int = 0
    error_rate_24h: float = 0.0
    uptime_30d: float = 100.0
    active_incidents: int = 0
    open_tickets: int = 0
    pending_invites: int = 0
    total_endpoints: int = 0
    documented_endpoints: int = 0

    @property
    def doc_coverage_pct(self) -> float:
        if self.total_endpoints == 0: return 0.0
        return round((self.documented_endpoints / self.total_endpoints) * 100, 1)

    @property
    def health_status(self) -> str:
        if self.active_incidents > 0 or self.error_rate_24h > 10: return "critical"
        if self.error_rate_24h > 5 or self.uptime_30d < 99.5: return "degraded"
        return "healthy"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlatformSummary:
    def __init__(self) -> None:
        self._summaries: dict[str, PlatformSummary] = {}

    def update(self, installation_id: str, summary: PlatformSummary) -> PlatformSummary:
        if not installation_id: raise ValueError("installation_id is required")
        self._summaries[installation_id] = summary
        return summary

    def get_summary(self, installation_id: str) -> PlatformSummary:
        return self._summaries.get(installation_id, PlatformSummary())

    def is_healthy(self, installation_id: str) -> bool:
        return self.get_summary(installation_id).health_status == "healthy"

    def needs_attention(self, installation_id: str) -> list[str]:
        s = self.get_summary(installation_id)
        issues: list[str] = []
        if s.active_incidents > 0: issues.append(f"{s.active_incidents} active incidents")
        if s.error_rate_24h > 5: issues.append(f"High error rate: {s.error_rate_24h}%")
        if s.open_tickets > 10: issues.append(f"{s.open_tickets} open tickets")
        if s.doc_coverage_pct < 80: issues.append(f"Low doc coverage: {s.doc_coverage_pct}%")
        if s.pending_invites > 5: issues.append(f"{s.pending_invites} pending invites")
        return issues
