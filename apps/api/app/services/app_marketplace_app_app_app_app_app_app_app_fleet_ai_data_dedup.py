"""Fleet AI Data Deduplication — track training data deduplication."""
from __future__ import annotations
def fleet_ai_data_dedup(dedupers: list[dict]) -> dict:
    active = [d for d in dedupers if d.get("active", True)]
    processed_24h = sum(d.get("processed_24h", 0) for d in dedupers)
    duplicates_removed = sum(d.get("removed", 0) for d in dedupers)
    reduction_pct = round(sum(d.get("reduction_pct", 0) for d in dedupers) / max(len(dedupers), 1), 1)
    return {"dedupers": len(dedupers), "active": len(active), "processed_24h": processed_24h,
            "removed": duplicates_removed, "reduction_pct": reduction_pct, "clean": reduction_pct > 0}
