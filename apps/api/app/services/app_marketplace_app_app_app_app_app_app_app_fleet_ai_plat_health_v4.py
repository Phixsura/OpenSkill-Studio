"""Fleet AI Platform Health v4 — track ultimate platform health overview."""
from __future__ import annotations
def fleet_ai_platform_health_v4(checkers: list[dict]) -> dict:
    active = [c for c in checkers if c.get("active", True)]
    services = sum(c.get("services", 0) for c in checkers)
    healthy = sum(c.get("healthy", 0) for c in checkers)
    uptime = round(sum(c.get("uptime_pct", 0) for c in checkers) / max(len(checkers), 1), 3)
    score = round(healthy / max(services, 1) * 100, 1)
    return {"checkers": len(checkers), "active": len(active), "services": services,
            "healthy": healthy, "uptime": uptime, "score": score, "green": score == 100}
