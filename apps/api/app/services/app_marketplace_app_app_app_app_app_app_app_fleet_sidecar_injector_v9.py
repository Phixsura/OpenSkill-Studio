"""Fleet Sidecar Injector v9 — track sidecar proxy injection status."""
from __future__ import annotations
def fleet_sidecar_injector_v9(namespaces: list[dict]) -> dict:
    injected = [n for n in namespaces if n.get("injected")]
    pods_with_sidecar = sum(n.get("pods_injected", 0) for n in namespaces)
    total_pods = sum(n.get("total_pods", 0) for n in namespaces)
    return {"namespaces": len(namespaces), "injected": len(injected),
            "pods_with_sidecar": pods_with_sidecar, "total_pods": total_pods,
            "healthy": pods_with_sidecar == total_pods}
