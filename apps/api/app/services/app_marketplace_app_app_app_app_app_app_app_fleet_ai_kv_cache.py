"""Fleet AI KV Cache — track key-value cache for transformer inference."""
from __future__ import annotations
def fleet_ai_kv_cache(caches: list[dict]) -> dict:
    active = [c for c in caches if c.get("active", True)]
    cache_size_gb = round(sum(c.get("size_gb", 0) for c in caches), 1)
    hit_rate = round(sum(c.get("hit_rate", 0) for c in caches) / max(len(caches), 1), 1)
    evictions_24h = sum(c.get("evictions_24h", 0) for c in caches)
    return {"caches": len(caches), "active": len(active), "size_gb": cache_size_gb,
            "hit_rate": hit_rate, "evictions_24h": evictions_24h, "hot": hit_rate > 80}
