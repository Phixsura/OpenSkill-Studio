"""Fleet Log Aggregation v9 — track centralized log collection."""
from __future__ import annotations
def fleet_log_aggregation_v9(collectors: list[dict]) -> dict:
    active = [c for c in collectors if c.get("active")]
    events_sec = sum(c.get("events_per_sec", 0) for c in collectors)
    storage_gb = sum(c.get("storage_gb", 0) for c in collectors)
    return {"collectors": len(collectors), "active": len(active), "events_per_sec": events_sec,
            "storage_gb": round(storage_gb, 1), "healthy": len(active) == len(collectors)}
