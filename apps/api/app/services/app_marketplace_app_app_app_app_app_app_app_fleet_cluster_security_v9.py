"""Fleet Cluster Security v9 — track K8s cluster security posture."""
from __future__ import annotations
def fleet_cluster_security_v9(clusters: list[dict]) -> dict:
    rbac_enabled = [c for c in clusters if c.get("rbac")]
    psa_enforced = [c for c in clusters if c.get("pod_security")]
    network_policies = [c for c in clusters if c.get("network_policies")]
    score = sum(c.get("security_score", 0) for c in clusters) / len(clusters) if clusters else 0
    return {"clusters": len(clusters), "rbac": len(rbac_enabled), "psa": len(psa_enforced),
            "net_policies": len(network_policies), "avg_score": round(score, 1), "healthy": score > 90}
