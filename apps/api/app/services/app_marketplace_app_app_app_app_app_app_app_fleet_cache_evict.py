"""Fleet cache eviction — track cache eviction rates."""
from __future__ import annotations
def fleet_cache_eviction(caches: list[dict]) -> dict:
    total_evictions = sum(c.get("evictions_per_sec", 0) for c in caches)
    high_evict = [c for c in caches if c.get("evictions_per_sec", 0) > 100]
    return {"total_evictions_per_sec": total_evictions, "caches": len(caches),
            "high_eviction": len(high_evict), "needs_resize": len(high_evict) > 0}
