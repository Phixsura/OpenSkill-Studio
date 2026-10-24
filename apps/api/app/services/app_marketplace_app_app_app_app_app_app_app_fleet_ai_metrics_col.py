"""Fleet AI Metrics Collector — track AI performance metrics aggregation."""
from __future__ import annotations
def fleet_ai_metrics_collector(collectors: list[dict]) -> dict:
    active = [c for c in collectors if c.get("active", True)]
    metrics_24h = sum(c.get("metrics_24h", 0) for c in collectors)
    series = sum(c.get("series", 0) for c in collectors)
    resolution_s = min((c.get("resolution_s", 9999) for c in collectors), default=9999)
    return {"collectors": len(collectors), "active": len(active), "metrics_24h": metrics_24h,
            "series": series, "resolution_s": resolution_s, "granular": resolution_s <= 10}
