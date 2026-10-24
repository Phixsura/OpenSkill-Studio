"""Cluster resource optimizer — optimize resource allocation across nodes."""
from __future__ import annotations


def optimize_allocation(nodes: list[dict], pods: list[dict]) -> dict:
    total_cpu = sum(n.get("cpu", 0) for n in nodes)
    total_mem = sum(n.get("memory_gb", 0) for n in nodes)
    requested_cpu = sum(p.get("cpu_request", 0) for p in pods)
    requested_mem = sum(p.get("memory_request_gb", 0) for p in pods)
    cpu_util = round(requested_cpu / max(total_cpu, 0.01) * 100, 1)
    mem_util = round(requested_mem / max(total_mem, 0.01) * 100, 1)
    over_provisioned = cpu_util < 30 and mem_util < 30
    under_provisioned = cpu_util > 80 or mem_util > 80
    recommendation = "scale_down" if over_provisioned else ("scale_up" if under_provisioned else "optimal")
    return {"total_cpu": total_cpu, "total_memory_gb": total_mem,
            "requested_cpu": requested_cpu, "requested_memory_gb": requested_mem,
            "cpu_util_pct": cpu_util, "mem_util_pct": mem_util,
            "recommendation": recommendation, "nodes": len(nodes), "pods": len(pods)}
