"""Fleet gateway rate limit — track rate limiting across API gateways."""
from __future__ import annotations
def fleet_gw_ratelimit(gateways: list[dict]) -> dict:
    limited = sum(g.get("requests_limited", 0) for g in gateways)
    total = sum(g.get("requests_total", 0) for g in gateways)
    pct = round(limited / max(total, 1) * 100, 2)
    return {"limited": limited, "total": total, "limited_pct": pct, "excessive": pct > 5}
