"""Fleet GraphQL Gateway v9 — track GraphQL query performance and caching."""
from __future__ import annotations
def fleet_graphql_gateway_v9(endpoints: list[dict]) -> dict:
    queries = sum(e.get("queries_per_sec", 0) for e in endpoints)
    mutations = sum(e.get("mutations_per_sec", 0) for e in endpoints)
    cache_hits = sum(e.get("cache_hit_pct", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    return {"endpoints": len(endpoints), "qps": queries, "mps": mutations,
            "cache_hit_pct": round(cache_hits, 1), "healthy": cache_hits > 50}
