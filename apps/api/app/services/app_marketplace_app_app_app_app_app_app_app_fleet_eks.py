"""Fleet EKS — track Amazon Elastic Kubernetes Service."""
from __future__ import annotations
def fleet_eks_status(clusters: list[dict]) -> dict:
    active = [c for c in clusters if c.get("status") == "ACTIVE"]
    fargate_profiles = sum(c.get("fargate_profiles", 0) for c in clusters)
    managed_nodegroups = sum(c.get("managed_nodegroups", 0) for c in clusters)
    return {"clusters": len(clusters), "active": len(active), "fargate_profiles": fargate_profiles,
            "managed_nodegroups": managed_nodegroups, "all_active": len(active) == len(clusters)}
