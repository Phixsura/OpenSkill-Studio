"""Fleet build cache — track build cache hit rates."""
from __future__ import annotations
def fleet_build_cache(builds: list[dict]) -> dict:
    hits = sum(b.get("cache_hits", 0) for b in builds)
    misses = sum(b.get("cache_misses", 0) for b in builds)
    total = hits + misses
    rate = round(hits / max(total, 1) * 100, 1)
    time_saved = sum(b.get("time_saved_sec", 0) for b in builds)
    return {"hit_rate_pct": rate, "time_saved_sec": time_saved, "builds": len(builds), "effective": rate >= 70}
