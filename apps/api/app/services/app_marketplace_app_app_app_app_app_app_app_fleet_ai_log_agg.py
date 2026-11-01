"""Fleet AI Log Aggregator — track centralized AI log collection."""
from __future__ import annotations
def fleet_ai_log_aggregator(aggregators: list[dict]) -> dict:
    active = [a for a in aggregators if a.get("active", True)]
    logs_24h = sum(a.get("logs_24h", 0) for a in aggregators)
    storage_gb = round(sum(a.get("storage_gb", 0) for a in aggregators), 1)
    sources = sum(a.get("sources", 0) for a in aggregators)
    return {"aggregators": len(aggregators), "active": len(active), "logs_24h": logs_24h,
            "storage_gb": storage_gb, "sources": sources, "collecting": logs_24h > 0}
