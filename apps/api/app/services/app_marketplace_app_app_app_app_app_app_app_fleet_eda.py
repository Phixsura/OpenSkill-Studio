"""Fleet EDA — event-driven architecture health."""
from __future__ import annotations
def fleet_eda_health(topics: list[dict]) -> dict:
    healthy = [t for t in topics if t.get("consumer_lag", 0) < 1000]
    total_events = sum(t.get("events_per_sec", 0) for t in topics)
    return {"topics": len(topics), "healthy": len(healthy), "unhealthy": len(topics) - len(healthy),
            "total_eps": total_events, "all_healthy": len(healthy) == len(topics)}
