"""Fleet CDN performance — track CDN hit rate and latency."""
from __future__ import annotations
def fleet_cdn_perf(pops: list[dict]) -> dict:
    hits = sum(p.get("hits", 0) for p in pops)
    misses = sum(p.get("misses", 0) for p in pops)
    total = hits + misses
    hit_rate = round(hits / max(total, 1) * 100, 1)
    avg_lat = round(sum(p.get("latency_ms", 0) for p in pops) / max(len(pops), 1), 1)
    return {"hit_rate_pct": hit_rate, "avg_latency_ms": avg_lat, "pops": len(pops), "effective": hit_rate >= 90}
