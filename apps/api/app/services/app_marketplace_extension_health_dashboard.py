"""Health Dashboard — aggregate health status across all platform services.

Collects health signals from extensions, connectors, sandboxes, and
infrastructure, computes overall platform health score, and identifies
top issues requiring attention.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    DOWN = "down"


HEALTH_WEIGHT = {HealthState.HEALTHY: 100, HealthState.DEGRADED: 60,
                 HealthState.CRITICAL: 20, HealthState.DOWN: 0}


@dataclass
class ServiceHealth:
    name: str
    category: str  # extension, connector, sandbox, infrastructure
    state: HealthState
    message: str = ""
    metric_value: float = 0.0  # e.g. uptime %, latency


@dataclass
class HealthAlert:
    service_name: str
    severity: str
    message: str
    suggested_action: str = ""


class HealthDashboardService:
    """Aggregates health status across all platform services."""

    def __init__(self):
        self._services: dict[str, ServiceHealth] = {}

    def report(self, name: str, category: str, state: HealthState,
               message: str = "", metric_value: float = 0.0) -> ServiceHealth:
        svc = ServiceHealth(
            name=name, category=category, state=state,
            message=message, metric_value=metric_value,
        )
        self._services[name] = svc
        return svc

    def get_overall_score(self) -> float:
        if not self._services:
            return 100.0
        total = sum(HEALTH_WEIGHT[s.state] for s in self._services.values())
        return round(total / len(self._services), 1)

    def get_overall_state(self) -> HealthState:
        score = self.get_overall_score()
        if score >= 90:
            return HealthState.HEALTHY
        if score >= 60:
            return HealthState.DEGRADED
        if score >= 20:
            return HealthState.CRITICAL
        return HealthState.DOWN

    def get_by_category(self) -> dict[str, list[ServiceHealth]]:
        result: dict[str, list[ServiceHealth]] = defaultdict(list)
        for svc in self._services.values():
            result[svc.category].append(svc)
        return dict(result)

    def get_issues(self) -> list[HealthAlert]:
        alerts: list[HealthAlert] = []
        for svc in self._services.values():
            if svc.state == HealthState.DOWN:
                alerts.append(HealthAlert(
                    service_name=svc.name, severity="critical",
                    message=f"{svc.name} is DOWN: {svc.message}",
                    suggested_action="Restart service or check infrastructure",
                ))
            elif svc.state == HealthState.CRITICAL:
                alerts.append(HealthAlert(
                    service_name=svc.name, severity="high",
                    message=f"{svc.name} is critical: {svc.message}",
                    suggested_action="Investigate root cause immediately",
                ))
            elif svc.state == HealthState.DEGRADED:
                alerts.append(HealthAlert(
                    service_name=svc.name, severity="medium",
                    message=f"{svc.name} is degraded: {svc.message}",
                    suggested_action="Monitor and plan remediation",
                ))
        alerts.sort(key=lambda a: {"critical": 0, "high": 1, "medium": 2}.get(a.severity, 3))
        return alerts

    def get_summary(self) -> dict:
        by_state: dict[str, int] = defaultdict(int)
        for svc in self._services.values():
            by_state[svc.state.value] += 1
        return {
            "total_services": len(self._services),
            "overall_score": self.get_overall_score(),
            "overall_state": self.get_overall_state().value,
            "by_state": dict(by_state),
            "categories": len(self.get_by_category()),
            "active_issues": len(self.get_issues()),
        }
