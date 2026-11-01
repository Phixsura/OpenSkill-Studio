"""Fleet event bus — track event bus throughput and lag."""
from __future__ import annotations
def fleet_eventbus_stats(topics: list[dict]) -> dict:
    total_rate = sum(t.get("events_per_sec", 0) for t in topics)
    max_lag = max((t.get("lag_ms", 0) for t in topics), default=0)
    return {"total_eps": round(total_rate, 1), "max_lag_ms": max_lag,
            "topics": len(topics), "lagging": max_lag > 5000}
