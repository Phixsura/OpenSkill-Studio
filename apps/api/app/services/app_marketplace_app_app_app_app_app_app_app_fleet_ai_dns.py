"""Fleet AI DNS Resolver — track AI service discovery via DNS."""
from __future__ import annotations
def fleet_ai_dns_resolver(resolvers: list[dict]) -> dict:
    active = [r for r in resolvers if r.get("active", True)]
    queries_24h = sum(r.get("queries_24h", 0) for r in resolvers)
    cache_hit_pct = round(sum(r.get("cache_hit_pct", 0) for r in resolvers) / max(len(resolvers), 1), 1)
    services_registered = sum(r.get("services", 0) for r in resolvers)
    return {"resolvers": len(resolvers), "active": len(active), "queries_24h": queries_24h,
            "cache_hit_pct": cache_hit_pct, "services": services_registered, "fast": cache_hit_pct > 90}
