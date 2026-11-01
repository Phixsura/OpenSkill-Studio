"""Fleet Tracing Collector v9 — track distributed tracing span collection."""
from __future__ import annotations
def fleet_tracing_collector_v9(collectors: list[dict]) -> dict:
    spans_sec = sum(c.get("spans_per_sec", 0) for c in collectors)
    dropped = sum(c.get("dropped", 0) for c in collectors)
    storage_gb = sum(c.get("storage_gb", 0) for c in collectors)
    return {"collectors": len(collectors), "spans_per_sec": spans_sec, "dropped": dropped,
            "storage_gb": round(storage_gb, 1), "healthy": dropped == 0}
