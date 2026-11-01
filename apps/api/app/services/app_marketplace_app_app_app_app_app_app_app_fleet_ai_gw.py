"""Fleet AI Gateway — track AI model routing and caching."""
from __future__ import annotations
def fleet_ai_gateway(gateways: list[dict]) -> dict:
    active = [g for g in gateways if g.get("active", True)]
    requests_24h = sum(g.get("requests_24h", 0) for g in gateways)
    cache_hit_rate = round(sum(g.get("cache_hit_pct", 0) for g in gateways) / max(len(gateways), 1), 1)
    tokens_saved = sum(g.get("tokens_saved_24h", 0) for g in gateways)
    return {"gateways": len(gateways), "active": len(active), "requests_24h": requests_24h,
            "cache_hit_rate": cache_hit_rate, "tokens_saved": tokens_saved}
