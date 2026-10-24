"""Fleet AI Health v6 — track ultimate platform health."""
from __future__ import annotations
def fleet_ai_health_v6(checkers: list[dict]) -> dict:
    active = [c for c in checkers if c.get("active", True)]
    services = sum(c.get("services", 0) for c in checkers)
    healthy = sum(c.get("healthy", 0) for c in checkers)
    uptime = round(sum(c.get("uptime", 0) for c in checkers) / max(len(checkers), 1), 4)
    return {"checkers": len(checkers), "active": len(active), "services": services,
            "healthy": healthy, "uptime": uptime, "perfect": healthy == services}
