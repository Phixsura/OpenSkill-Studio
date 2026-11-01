"""Fleet AI Health Aggregator — track unified health status across all AI services."""
from __future__ import annotations
def fleet_ai_health_aggregator(aggregators: list[dict]) -> dict:
    active = [a for a in aggregators if a.get("active", True)]
    services = sum(a.get("services", 0) for a in aggregators)
    healthy = sum(a.get("healthy", 0) for a in aggregators)
    degraded = sum(a.get("degraded", 0) for a in aggregators)
    down = sum(a.get("down", 0) for a in aggregators)
    health_pct = round(healthy / max(services, 1) * 100, 1)
    return {"aggregators": len(aggregators), "active": len(active), "services": services,
            "healthy": healthy, "degraded": degraded, "down": down, "health_pct": health_pct, "green": down == 0}
