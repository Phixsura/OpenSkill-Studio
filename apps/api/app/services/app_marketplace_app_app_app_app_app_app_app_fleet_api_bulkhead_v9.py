"""Fleet API Bulkhead v9 — track bulkhead pattern isolation."""
from __future__ import annotations
def fleet_api_bulkhead_v9(bulkheads: list[dict]) -> dict:
    active = [b for b in bulkheads if b.get("active")]
    rejections = sum(b.get("rejections_today", 0) for b in bulkheads)
    avg_utilization = sum(b.get("utilization_pct", 0) for b in bulkheads) / len(bulkheads) if bulkheads else 0
    return {"bulkheads": len(bulkheads), "active": len(active), "rejections_today": rejections,
            "avg_utilization_pct": round(avg_utilization, 1), "healthy": rejections < 100}
