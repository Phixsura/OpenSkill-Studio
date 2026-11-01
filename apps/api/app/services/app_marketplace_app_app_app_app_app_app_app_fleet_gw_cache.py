"""Fleet gateway caching — track API response caching."""
from __future__ import annotations
def fleet_gw_cache(endpoints: list[dict]) -> dict:
    cached = [e for e in endpoints if e.get("cache_enabled", False)]
    total_hits = sum(e.get("cache_hits", 0) for e in cached)
    total_misses = sum(e.get("cache_misses", 0) for e in cached)
    rate = round(total_hits / max(total_hits + total_misses, 1) * 100, 1)
    return {"total": len(endpoints), "cached": len(cached), "hit_rate": rate, "effective": rate >= 80}
