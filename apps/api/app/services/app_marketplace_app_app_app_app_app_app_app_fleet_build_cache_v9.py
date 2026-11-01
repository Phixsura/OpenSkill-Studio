"""Fleet Build Cache v9 — track CI/CD build cache hit rates."""
from __future__ import annotations
def fleet_build_cache_v9(caches: list[dict]) -> dict:
    hits = sum(c.get("hits", 0) for c in caches)
    misses = sum(c.get("misses", 0) for c in caches)
    size_gb = sum(c.get("size_gb", 0) for c in caches)
    hit_rate = round(hits / (hits + misses) * 100, 1) if (hits + misses) else 0
    return {"caches": len(caches), "hit_rate": hit_rate, "size_gb": round(size_gb, 1),
            "time_saved_min": sum(c.get("time_saved_min", 0) for c in caches), "healthy": hit_rate > 70}
