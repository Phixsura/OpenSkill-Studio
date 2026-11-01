"""Fleet Namespace Manager v9 — track K8s namespace isolation and quotas."""
from __future__ import annotations
def fleet_namespace_mgr_v9(namespaces: list[dict]) -> dict:
    active = [n for n in namespaces if n.get("active", True)]
    quota_set = [n for n in namespaces if n.get("quota_set")]
    pods = sum(n.get("pod_count", 0) for n in namespaces)
    return {"total": len(namespaces), "active": len(active), "quota_set": len(quota_set),
            "total_pods": pods, "healthy": len(quota_set) == len(namespaces)}
