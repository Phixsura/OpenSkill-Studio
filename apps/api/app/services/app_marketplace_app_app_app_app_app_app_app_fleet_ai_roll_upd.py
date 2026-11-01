"""Fleet AI Rolling Update — track zero-downtime AI service updates."""
from __future__ import annotations
def fleet_ai_rolling_update(updaters: list[dict]) -> dict:
    active = [u for u in updaters if u.get("active", True)]
    updates_24h = sum(u.get("updates_24h", 0) for u in updaters)
    instances_updated = sum(u.get("instances", 0) for u in updaters)
    rollbacks = sum(u.get("rollbacks", 0) for u in updaters)
    return {"updaters": len(updaters), "active": len(active), "updates_24h": updates_24h,
            "instances": instances_updated, "rollbacks": rollbacks, "smooth": rollbacks == 0}
