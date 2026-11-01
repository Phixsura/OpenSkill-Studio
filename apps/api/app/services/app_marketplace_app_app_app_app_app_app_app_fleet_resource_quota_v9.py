"""Fleet Resource Quota v9 — track K8s resource quota enforcement."""
from __future__ import annotations
def fleet_resource_quota_v9(quotas: list[dict]) -> dict:
    cpu_used = sum(q.get("cpu_used", 0) for q in quotas)
    cpu_limit = sum(q.get("cpu_limit", 0) for q in quotas)
    mem_used_gb = sum(q.get("mem_used_gb", 0) for q in quotas)
    mem_limit_gb = sum(q.get("mem_limit_gb", 0) for q in quotas)
    return {"quotas": len(quotas), "cpu_used": cpu_used, "cpu_limit": cpu_limit,
            "mem_used_gb": round(mem_used_gb, 1), "mem_limit_gb": round(mem_limit_gb, 1),
            "healthy": cpu_used < cpu_limit * 0.9}
