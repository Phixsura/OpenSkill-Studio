"""Fleet DNS Resolver v9 — track DNS resolution health across zones."""
from __future__ import annotations
def fleet_dns_resolver_v9(zones: list[dict]) -> dict:
    active = [z for z in zones if z.get("active", True)]
    queries = sum(z.get("queries_per_sec", 0) for z in zones)
    return {"total_zones": len(zones), "active": len(active), "qps": queries,
            "avg_ttl": round(sum(z.get("ttl", 300) for z in zones) / len(zones)) if zones else 0,
            "healthy": len(active) == len(zones)}
