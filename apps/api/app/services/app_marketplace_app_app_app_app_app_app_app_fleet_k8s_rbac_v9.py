"""Fleet K8s RBAC v9 — track Kubernetes RBAC policy management."""
from __future__ import annotations
def fleet_k8s_rbac_v9(roles: list[dict]) -> dict:
    cluster_roles = [r for r in roles if r.get("type") == "ClusterRole"]
    role_bindings = sum(r.get("bindings", 0) for r in roles)
    over_privileged = [r for r in roles if r.get("over_privileged")]
    return {"roles": len(roles), "cluster_roles": len(cluster_roles), "bindings": role_bindings,
            "over_privileged": len(over_privileged), "healthy": len(over_privileged) == 0}
