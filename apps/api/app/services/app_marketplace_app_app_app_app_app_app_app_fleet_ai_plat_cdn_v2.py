"""Fleet AI CDN v2 — track AI model and data content delivery at scale."""
from __future__ import annotations
def fleet_ai_cdn_v2(cdns: list[dict]) -> dict:
    active = [c for c in cdns if c.get("active", True)]
    pops = sum(c.get("pops", 0) for c in cdns)
    bandwidth_tb = round(sum(c.get("bandwidth_tb", 0) for c in cdns), 1)
    cache_hit = round(sum(c.get("cache_hit_pct", 0) for c in cdns) / max(len(cdns), 1), 1)
    return {"cdns": len(cdns), "active": len(active), "pops": pops,
            "bandwidth_tb": bandwidth_tb, "cache_hit": cache_hit, "performant": cache_hit > 90}
