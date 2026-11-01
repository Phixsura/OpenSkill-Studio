"""Cache manager — manage application cache layers."""


def get_cache_stats(*, caches: list[dict]) -> dict:
    results = []
    total_hits = 0
    total_misses = 0
    for c in caches:
        hits = c.get("hits", 0)
        misses = c.get("misses", 0)
        total = hits + misses
        hit_rate = round(hits / max(total, 1) * 100, 1)
        total_hits += hits
        total_misses += misses
        results.append({
            "name": c["name"],
            "type": c.get("type", "memory"),
            "size_mb": c.get("size_mb", 0),
            "max_size_mb": c.get("max_size_mb", 256),
            "hits": hits,
            "misses": misses,
            "hit_rate": hit_rate,
            "evictions": c.get("evictions", 0),
            "ttl_sec": c.get("ttl_sec", 300),
        })
    overall_rate = round(total_hits / max(total_hits + total_misses, 1) * 100, 1)
    return {"caches": results, "total_caches": len(results),
            "overall_hit_rate": overall_rate}


def invalidate_cache(*, cache_name: str, pattern: str = "*") -> dict:
    return {"cache": cache_name, "pattern": pattern,
            "status": "invalidated", "keys_affected": "all" if pattern == "*" else "partial"}
