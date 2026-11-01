"""Fleet cache hit ratio — track cache effectiveness fleet-wide."""
from __future__ import annotations
def fleet_cache_ratio(caches: list[dict]) -> dict:
    hits = sum(c.get("hits", 0) for c in caches)
    misses = sum(c.get("misses", 0) for c in caches)
    total = hits + misses
    ratio = round(hits / max(total, 1) * 100, 1)
    return {"hits": hits, "misses": misses, "ratio_pct": ratio, "effective": ratio >= 80}
