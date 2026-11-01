"""Fleet Container Orchestrator v9 — track K8s control plane health."""
from __future__ import annotations
def fleet_container_orchestrator_v9(clusters: list[dict]) -> dict:
    healthy_cp = [c for c in clusters if c.get("control_plane_healthy")]
    etcd_healthy = [c for c in clusters if c.get("etcd_healthy")]
    api_server_latency = sum(c.get("api_server_latency_ms", 0) for c in clusters) / len(clusters) if clusters else 0
    return {"clusters": len(clusters), "control_plane_ok": len(healthy_cp), "etcd_ok": len(etcd_healthy),
            "avg_api_latency_ms": round(api_server_latency, 1), "healthy": len(healthy_cp) == len(clusters)}
