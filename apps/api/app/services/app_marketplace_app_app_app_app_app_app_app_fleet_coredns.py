"""Fleet CoreDNS — track cluster DNS health."""
from __future__ import annotations
def fleet_coredns_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    total_qps = sum(i.get("qps", 0) for i in instances)
    cache_hit_pct = round(sum(i.get("cache_hit_pct", 0) for i in instances) / max(len(instances), 1), 1)
    return {"instances": len(instances), "healthy": len(healthy), "qps": total_qps,
            "cache_hit_pct": cache_hit_pct, "all_healthy": len(healthy) == len(instances)}
