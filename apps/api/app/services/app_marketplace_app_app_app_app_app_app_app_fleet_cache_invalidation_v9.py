"""Fleet Cache Invalidation v9 — track cache invalidation patterns."""
from __future__ import annotations
def fleet_cache_invalidation_v9(caches: list[dict]) -> dict:
    invalidations = sum(c.get("invalidations_today", 0) for c in caches)
    cascade = sum(c.get("cascade_invalidations", 0) for c in caches)
    stale_reads = sum(c.get("stale_reads", 0) for c in caches)
    return {"caches": len(caches), "invalidations_today": invalidations,
            "cascade": cascade, "stale_reads": stale_reads, "healthy": stale_reads == 0}
