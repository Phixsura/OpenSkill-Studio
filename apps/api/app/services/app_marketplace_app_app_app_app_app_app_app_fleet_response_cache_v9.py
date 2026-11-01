"""Fleet Response Cache v9 — track API response caching performance."""
from __future__ import annotations
def fleet_response_cache_v9(caches: list[dict]) -> dict:
    hits = sum(c.get("hits", 0) for c in caches)
    misses = sum(c.get("misses", 0) for c in caches)
    hit_rate = round(hits / (hits + misses) * 100, 1) if (hits + misses) else 0
    bytes_saved = sum(c.get("bytes_saved_gb", 0) for c in caches)
    return {"caches": len(caches), "hit_rate": hit_rate, "bytes_saved_gb": round(bytes_saved, 1),
            "total_hits": hits, "healthy": hit_rate > 80}
