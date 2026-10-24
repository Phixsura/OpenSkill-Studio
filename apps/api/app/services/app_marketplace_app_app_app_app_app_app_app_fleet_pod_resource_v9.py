"""Fleet Pod Resource v9 — track pod CPU and memory resource usage."""
from __future__ import annotations
def fleet_pod_resource_v9(pods: list[dict]) -> dict:
    cpu_used = sum(p.get("cpu_millicores", 0) for p in pods)
    cpu_requested = sum(p.get("cpu_requested", 0) for p in pods)
    mem_used = sum(p.get("mem_mb", 0) for p in pods)
    mem_requested = sum(p.get("mem_requested", 0) for p in pods)
    return {"pods": len(pods), "cpu_used_m": cpu_used, "cpu_requested_m": cpu_requested,
            "mem_used_mb": mem_used, "mem_requested_mb": mem_requested,
            "healthy": cpu_used < cpu_requested * 0.9 if cpu_requested else True}
