"""Platform Command Center — unified platform overview combining key metrics."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ServiceStatus:
    service_name: str
    status: str  # operational, degraded, outage
    uptime_pct: float = 100.0
    active_incidents: int = 0
    last_checked: str = ""


@dataclass
class PlatformMetrics:
    total_consumers: int = 0
    total_endpoints: int = 0
    total_requests_24h: int = 0
    avg_latency_ms: float = 0.0
    error_rate_pct: float = 0.0
    active_api_keys: int = 0
    webhooks_active: int = 0
    sandbox_count: int = 0


@dataclass
class CommandCenter:
    """Unified platform overview combining services, metrics, and alerts."""

    _services: dict[str, ServiceStatus] = field(default_factory=dict)
    _metrics: PlatformMetrics = field(default_factory=PlatformMetrics)
    _alerts: list[dict] = field(default_factory=list)

    def register_service(self, service: ServiceStatus) -> dict:
        self._services[service.service_name] = service
        logger.info("service_registered", service=service.service_name)
        return {"service": service.service_name, "status": service.status}

    def update_status(self, service_name: str, status: str,
                      uptime_pct: float | None = None) -> dict:
        svc = self._services.get(service_name)
        if not svc:
            raise ValueError(f"Service {service_name} not registered")
        if status not in ("operational", "degraded", "outage"):
            raise ValueError(f"Invalid status: {status}")
        old_status = svc.status
        svc.status = status
        if uptime_pct is not None:
            svc.uptime_pct = uptime_pct
        if old_status != status:
            self._alerts.append({
                "type": "status_change", "service": service_name,
                "from": old_status, "to": status,
            })
        return {"service": service_name, "status": status, "changed": old_status != status}

    def update_metrics(self, **kwargs) -> dict:
        for key, value in kwargs.items():
            if hasattr(self._metrics, key):
                setattr(self._metrics, key, value)
        return {"updated": True}

    def add_alert(self, alert_type: str, message: str, severity: str = "info") -> dict:
        alert = {"type": alert_type, "message": message, "severity": severity}
        self._alerts.append(alert)
        return {"added": True, "total_alerts": len(self._alerts)}

    def get_overview(self) -> dict:
        services = list(self._services.values())
        operational = sum(1 for s in services if s.status == "operational")
        degraded = sum(1 for s in services if s.status == "degraded")
        outage = sum(1 for s in services if s.status == "outage")
        if outage > 0:
            platform_status = "major_outage"
        elif degraded > 0:
            platform_status = "partial_outage"
        else:
            platform_status = "all_operational"
        return {
            "platform_status": platform_status,
            "services": {
                "total": len(services),
                "operational": operational,
                "degraded": degraded,
                "outage": outage,
            },
            "metrics": {
                "total_consumers": self._metrics.total_consumers,
                "total_endpoints": self._metrics.total_endpoints,
                "requests_24h": self._metrics.total_requests_24h,
                "avg_latency_ms": self._metrics.avg_latency_ms,
                "error_rate_pct": self._metrics.error_rate_pct,
                "active_api_keys": self._metrics.active_api_keys,
                "webhooks_active": self._metrics.webhooks_active,
            },
            "recent_alerts": self._alerts[-5:],
        }

    def get_service_list(self) -> list[dict]:
        return [
            {"name": s.service_name, "status": s.status, "uptime": s.uptime_pct,
             "incidents": s.active_incidents}
            for s in sorted(self._services.values(), key=lambda x: x.service_name)
        ]

    def get_health_score(self) -> dict:
        services = list(self._services.values())
        if not services:
            return {"score": 100, "grade": "A"}
        avg_uptime = sum(s.uptime_pct for s in services) / len(services)
        penalty = sum(10 for s in services if s.status == "degraded")
        penalty += sum(25 for s in services if s.status == "outage")
        score = max(0, min(100, avg_uptime - penalty))
        if score >= 99:
            grade = "A"
        elif score >= 95:
            grade = "B"
        elif score >= 90:
            grade = "C"
        elif score >= 80:
            grade = "D"
        else:
            grade = "F"
        return {"score": round(score, 1), "grade": grade, "services_count": len(services)}
