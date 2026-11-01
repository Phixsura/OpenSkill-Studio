"""Consumer API Capacity Planner — capacity planning with growth projection."""
from __future__ import annotations

import math
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ResourceMetric:
    resource: str  # cpu, memory, storage, bandwidth, connections
    current_usage: float
    max_capacity: float
    unit: str = ""


@dataclass
class CapacityPlanner:
    """Plan capacity based on current usage and growth projections."""

    _resources: dict[str, ResourceMetric] = field(default_factory=dict)
    _history: dict[str, list[float]] = field(default_factory=dict)  # resource -> usage history

    def set_resource(self, metric: ResourceMetric) -> dict:
        if metric.max_capacity <= 0:
            raise ValueError("max_capacity must be positive")
        if metric.current_usage < 0:
            raise ValueError("current_usage must be non-negative")
        self._resources[metric.resource] = metric
        self._history.setdefault(metric.resource, []).append(metric.current_usage)
        utilization = round(metric.current_usage / metric.max_capacity * 100, 1)
        logger.info("resource_set", resource=metric.resource, utilization=utilization)
        return {"resource": metric.resource, "utilization_pct": utilization}

    def get_utilization(self, resource: str) -> dict:
        m = self._resources.get(resource)
        if not m:
            return {"resource": resource, "error": "not_found"}
        pct = round(m.current_usage / m.max_capacity * 100, 1)
        if pct >= 90:
            status = "critical"
        elif pct >= 75:
            status = "warning"
        else:
            status = "healthy"
        return {
            "resource": resource, "current": m.current_usage,
            "capacity": m.max_capacity, "utilization_pct": pct,
            "headroom": round(m.max_capacity - m.current_usage, 2),
            "status": status, "unit": m.unit,
        }

    def forecast(self, resource: str, growth_rate_pct: float = 10.0,
                 periods: int = 6) -> dict:
        m = self._resources.get(resource)
        if not m:
            return {"resource": resource, "error": "not_found"}
        if growth_rate_pct < 0:
            raise ValueError("growth_rate_pct must be non-negative")
        projections = []
        current = m.current_usage
        rate = growth_rate_pct / 100
        exhaust_period = None
        for i in range(1, periods + 1):
            projected = current * (1 + rate) ** i
            pct = round(projected / m.max_capacity * 100, 1)
            projections.append({"period": i, "projected_usage": round(projected, 2),
                                "utilization_pct": min(pct, 100)})
            if exhaust_period is None and projected >= m.max_capacity:
                exhaust_period = i
        return {
            "resource": resource,
            "current_usage": m.current_usage,
            "capacity": m.max_capacity,
            "growth_rate_pct": growth_rate_pct,
            "projections": projections,
            "periods_to_exhaustion": exhaust_period,
            "action_needed": exhaust_period is not None and exhaust_period <= 3,
        }

    def recommend_scaling(self, target_utilization_pct: float = 70.0) -> list[dict]:
        recommendations = []
        for resource, m in self._resources.items():
            current_pct = m.current_usage / m.max_capacity * 100
            if current_pct > target_utilization_pct:
                needed = m.current_usage / (target_utilization_pct / 100)
                scale_factor = round(needed / m.max_capacity, 2)
                recommendations.append({
                    "resource": resource,
                    "current_utilization": round(current_pct, 1),
                    "target_utilization": target_utilization_pct,
                    "recommended_capacity": round(needed, 2),
                    "scale_factor": scale_factor,
                })
        recommendations.sort(key=lambda x: x["current_utilization"], reverse=True)
        return recommendations

    def get_overview(self) -> dict:
        resources = []
        for name in sorted(self._resources):
            resources.append(self.get_utilization(name))
        critical = sum(1 for r in resources if r.get("status") == "critical")
        warning = sum(1 for r in resources if r.get("status") == "warning")
        return {
            "total_resources": len(resources),
            "critical": critical,
            "warning": warning,
            "healthy": len(resources) - critical - warning,
            "resources": resources,
        }
