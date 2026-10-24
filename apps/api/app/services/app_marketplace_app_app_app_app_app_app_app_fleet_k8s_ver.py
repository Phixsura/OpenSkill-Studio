"""Fleet k8s version — track Kubernetes version distribution."""
from __future__ import annotations
def fleet_k8s_version(nodes: list[dict]) -> dict:
    versions: dict[str, int] = {}
    for n in nodes:
        v = n.get("k8s_version", "unknown")
        versions[v] = versions.get(v, 0) + 1
    skewed = len(versions) > 1
    return {"total": len(nodes), "versions": versions, "skewed": skewed, "version_count": len(versions)}
