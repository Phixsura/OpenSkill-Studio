"""Fleet AI Liveness Checker — track AI service liveness monitoring."""
from __future__ import annotations
def fleet_ai_liveness(checkers: list[dict]) -> dict:
    active = [c for c in checkers if c.get("active", True)]
    services = sum(c.get("services", 0) for c in checkers)
    alive = sum(c.get("alive", 0) for c in checkers)
    restarts_24h = sum(c.get("restarts", 0) for c in checkers)
    return {"checkers": len(checkers), "active": len(active), "services": services,
            "alive": alive, "restarts": restarts_24h, "stable": restarts_24h < 5}
