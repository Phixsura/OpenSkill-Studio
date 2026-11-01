"""Fleet distributed lock — track lock contention and deadlocks."""
from __future__ import annotations
def fleet_dist_lock(stats: dict) -> dict:
    active = stats.get("active_locks", 0)
    contention = stats.get("contention_events_24h", 0)
    deadlocks = stats.get("deadlocks_24h", 0)
    return {"active_locks": active, "contention": contention, "deadlocks": deadlocks,
            "healthy": deadlocks == 0 and contention < 100}
