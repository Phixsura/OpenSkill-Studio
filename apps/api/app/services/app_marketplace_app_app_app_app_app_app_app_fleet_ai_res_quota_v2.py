"""Fleet AI Resource Quota v2 — track advanced per-namespace resource limits."""
from __future__ import annotations
def fleet_ai_resource_quota_v2(quotas: list[dict]) -> dict:
    active = [q for q in quotas if q.get("active", True)]
    namespaces = sum(q.get("namespaces", 0) for q in quotas)
    gpu_allocated = sum(q.get("gpus", 0) for q in quotas)
    memory_gb = round(sum(q.get("memory_gb", 0) for q in quotas), 1)
    return {"quotas": len(quotas), "active": len(active), "namespaces": namespaces,
            "gpus": gpu_allocated, "memory_gb": memory_gb, "governed": namespaces > 0}
