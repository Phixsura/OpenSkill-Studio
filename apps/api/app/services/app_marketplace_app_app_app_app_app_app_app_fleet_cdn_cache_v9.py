"""Fleet CDN Cache v9 — track CDN cache hit ratios and edge pop health."""
from __future__ import annotations
def fleet_cdn_cache_v9(pops: list[dict]) -> dict:
    hit_ratio = sum(p.get("hit_ratio", 0) for p in pops) / len(pops) if pops else 0
    bandwidth_gbps = sum(p.get("bandwidth_gbps", 0) for p in pops)
    errors = sum(p.get("errors", 0) for p in pops)
    return {"pops": len(pops), "avg_hit_ratio": round(hit_ratio, 2), "bandwidth_gbps": round(bandwidth_gbps, 1),
            "errors": errors, "healthy": errors == 0}
