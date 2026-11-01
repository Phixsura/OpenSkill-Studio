"""Fleet adaptive concurrency — track concurrency limit adaptation."""
from __future__ import annotations
def fleet_adaptive_concurrency(services: list[dict]) -> dict:
    total_limit = sum(s.get("current_limit", 0) for s in services)
    avg_limit = round(total_limit / max(len(services), 1), 1)
    adjusted = [s for s in services if s.get("recently_adjusted", False)]
    return {"services": len(services), "avg_limit": avg_limit, "recently_adjusted": len(adjusted),
            "stable": len(adjusted) == 0}
