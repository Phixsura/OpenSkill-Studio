"""Consumer API Health Dashboard — unified consumer health view."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class HealthIndicator:
    name: str
    status: str  # "healthy", "degraded", "critical"
    value: float
    threshold: float
    unit: str = ""

@dataclass
class HealthDashboard:
    consumer_id: str
    overall_status: str  # "healthy", "degraded", "critical"
    health_score: float  # 0-100
    indicators: list[HealthIndicator] = field(default_factory=list)
    active_alerts: int = 0
    active_incidents: int = 0

STATUS_PRIORITY = {"critical": 0, "degraded": 1, "healthy": 2}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[tuple[str, str], HealthDashboard] = {}

    def compute(self, installation_id: str, consumer_id: str, error_rate: float, avg_latency_ms: float, uptime_pct: float, active_alerts: int = 0, active_incidents: int = 0) -> HealthDashboard:
        if not installation_id:
            raise ValueError("installation_id is required")
        indicators: list[HealthIndicator] = []
        # Error rate
        if error_rate > 5:
            indicators.append(HealthIndicator(name="Error Rate", status="critical", value=error_rate, threshold=5, unit="%"))
        elif error_rate > 1:
            indicators.append(HealthIndicator(name="Error Rate", status="degraded", value=error_rate, threshold=1, unit="%"))
        else:
            indicators.append(HealthIndicator(name="Error Rate", status="healthy", value=error_rate, threshold=1, unit="%"))
        # Latency
        if avg_latency_ms > 1000:
            indicators.append(HealthIndicator(name="Latency", status="critical", value=avg_latency_ms, threshold=1000, unit="ms"))
        elif avg_latency_ms > 500:
            indicators.append(HealthIndicator(name="Latency", status="degraded", value=avg_latency_ms, threshold=500, unit="ms"))
        else:
            indicators.append(HealthIndicator(name="Latency", status="healthy", value=avg_latency_ms, threshold=500, unit="ms"))
        # Uptime
        if uptime_pct < 99:
            indicators.append(HealthIndicator(name="Uptime", status="critical", value=uptime_pct, threshold=99, unit="%"))
        elif uptime_pct < 99.9:
            indicators.append(HealthIndicator(name="Uptime", status="degraded", value=uptime_pct, threshold=99.9, unit="%"))
        else:
            indicators.append(HealthIndicator(name="Uptime", status="healthy", value=uptime_pct, threshold=99.9, unit="%"))
        # Overall
        worst = min(STATUS_PRIORITY.get(i.status, 2) for i in indicators)
        overall = {0: "critical", 1: "degraded", 2: "healthy"}[worst]
        healthy_count = sum(1 for i in indicators if i.status == "healthy")
        score = round(healthy_count / len(indicators) * 100, 1)
        dashboard = HealthDashboard(consumer_id=consumer_id, overall_status=overall, health_score=score, indicators=indicators, active_alerts=active_alerts, active_incidents=active_incidents)
        self._dashboards[(installation_id, consumer_id)] = dashboard
        return dashboard

    def get(self, installation_id: str, consumer_id: str) -> HealthDashboard | None:
        return self._dashboards.get((installation_id, consumer_id))

    def list_critical(self, installation_id: str) -> list[HealthDashboard]:
        return [d for (inst, _), d in self._dashboards.items() if inst == installation_id and d.overall_status == "critical"]
