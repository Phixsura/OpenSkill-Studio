"""Fleet AI CDN — track AI model and asset content delivery."""
from __future__ import annotations
def fleet_ai_cdn(cdns: list[dict]) -> dict:
    active = [c for c in cdns if c.get("active", True)]
    pops = sum(c.get("pops", 0) for c in cdns)
    bandwidth_tb = round(sum(c.get("bandwidth_tb", 0) for c in cdns), 1)
    cache_hit_pct = round(sum(c.get("cache_hit_pct", 0) for c in cdns) / max(len(cdns), 1), 1)
    return {"cdns": len(cdns), "active": len(active), "pops": pops,
            "bandwidth_tb": bandwidth_tb, "cache_hit_pct": cache_hit_pct, "efficient": cache_hit_pct > 90}
