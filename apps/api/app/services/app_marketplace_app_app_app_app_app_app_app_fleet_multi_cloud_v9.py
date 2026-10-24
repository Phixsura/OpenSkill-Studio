"""Fleet Multi-Cloud v9 — track workloads across cloud providers."""
from __future__ import annotations
def fleet_multi_cloud_v9(providers: list[dict]) -> dict:
    active = [p for p in providers if p.get("active", True)]
    instances = sum(p.get("instances", 0) for p in providers)
    spend = sum(p.get("monthly_spend", 0) for p in providers)
    return {"providers": len(providers), "active": len(active), "total_instances": instances,
            "monthly_spend": round(spend, 2), "healthy": len(active) == len(providers)}
