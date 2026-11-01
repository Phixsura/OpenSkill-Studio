"""Fleet AI CDN v8 — track ultimate content delivery at scale."""
from __future__ import annotations
def fleet_ai_cdn_v8(cdns: list[dict]) -> dict:
    active = [c for c in cdns if c.get("active", True)]
    pops = sum(c.get("pops", 0) for c in cdns)
    bandwidth_pbps = round(sum(c.get("pbps", 0) for c in cdns), 1)
    cache_hit = round(sum(c.get("hit_pct", 0) for c in cdns) / max(len(cdns), 1), 1)
    return {"cdns": len(cdns), "active": len(active), "pops": pops,
            "pbps": bandwidth_pbps, "hit_pct": cache_hit, "optimal": cache_hit > 95}
