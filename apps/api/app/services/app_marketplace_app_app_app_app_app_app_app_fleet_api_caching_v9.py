"""Fleet API Caching v9 — track API response caching strategies."""
from __future__ import annotations
def fleet_api_caching_v9(endpoints: list[dict]) -> dict:
    cached = [e for e in endpoints if e.get("cached")]
    hit_rate = sum(e.get("cache_hit_pct", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    bytes_saved = sum(e.get("bytes_saved_mb", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "cached": len(cached), "avg_hit_rate": round(hit_rate, 1),
            "bytes_saved_mb": round(bytes_saved, 1), "healthy": hit_rate > 70}
