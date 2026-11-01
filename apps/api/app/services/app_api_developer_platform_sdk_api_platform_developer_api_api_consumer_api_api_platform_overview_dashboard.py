"""API Platform Overview Dashboard — unified dashboard for the entire API platform."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PlatformOverview:
    total_consumers: int = 0
    active_consumers_24h: int = 0
    total_endpoints: int = 0
    total_requests_24h: int = 0
    overall_uptime_pct: float = 100.0
    overall_error_rate_pct: float = 0.0
    avg_latency_ms: float = 0.0
    open_incidents: int = 0
    pending_invites: int = 0
    webhook_success_rate: float = 100.0
    revenue_this_month_cents: int = 0

    @property
    def health(self) -> str:
        if self.open_incidents > 0 or self.overall_error_rate_pct > 10: return "critical"
        if self.overall_error_rate_pct > 5 or self.overall_uptime_pct < 99.5: return "degraded"
        return "healthy"

    @property
    def revenue_dollars(self) -> str:
        return f"${self.revenue_this_month_cents / 100:,.2f}"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPlatformOverviewDashboard:
    def __init__(self) -> None:
        self._overviews: dict[str, PlatformOverview] = {}

    def update(self, installation_id: str, overview: PlatformOverview) -> PlatformOverview:
        if not installation_id: raise ValueError("installation_id is required")
        self._overviews[installation_id] = overview
        return overview

    def get_overview(self, installation_id: str) -> PlatformOverview:
        return self._overviews.get(installation_id, PlatformOverview())

    def alerts(self, installation_id: str) -> list[str]:
        o = self.get_overview(installation_id)
        alerts: list[str] = []
        if o.open_incidents > 0: alerts.append(f"🔴 {o.open_incidents} active incidents")
        if o.overall_error_rate_pct > 5: alerts.append(f"⚠️ High error rate: {o.overall_error_rate_pct}%")
        if o.overall_uptime_pct < 99.9: alerts.append(f"📉 Uptime below SLA: {o.overall_uptime_pct}%")
        if o.webhook_success_rate < 95: alerts.append(f"🔔 Low webhook success: {o.webhook_success_rate}%")
        return alerts
