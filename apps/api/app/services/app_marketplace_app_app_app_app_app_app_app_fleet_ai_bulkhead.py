"""Fleet AI Bulkhead Pattern — track service isolation bulkheads."""
from __future__ import annotations
def fleet_ai_bulkhead(bulkheads: list[dict]) -> dict:
    active = [b for b in bulkheads if b.get("active", True)]
    partitions = sum(b.get("partitions", 0) for b in bulkheads)
    rejections_24h = sum(b.get("rejections_24h", 0) for b in bulkheads)
    isolation_pct = round(sum(b.get("isolation_pct", 0) for b in bulkheads) / max(len(bulkheads), 1), 1)
    return {"bulkheads": len(bulkheads), "active": len(active), "partitions": partitions,
            "rejections_24h": rejections_24h, "isolation_pct": isolation_pct, "isolated": isolation_pct == 100}
