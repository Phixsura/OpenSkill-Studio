"""Fleet AI Health v5 — track ultimate platform health and wellness."""
from __future__ import annotations
def fleet_ai_health_v5(checkers: list[dict]) -> dict:
    active = [c for c in checkers if c.get("active", True)]
    services = sum(c.get("services", 0) for c in checkers)
    healthy = sum(c.get("healthy", 0) for c in checkers)
    score = round(healthy / max(services, 1) * 100, 2)
    uptime = round(sum(c.get("uptime_pct", 0) for c in checkers) / max(len(checkers), 1), 4)
    return {"checkers": len(checkers), "active": len(active), "services": services,
            "healthy": healthy, "score": score, "uptime": uptime, "perfect": score == 100}
