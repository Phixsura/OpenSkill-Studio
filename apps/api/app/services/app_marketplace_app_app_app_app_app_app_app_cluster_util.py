"""Cluster utilization — track resource utilization across clusters."""
from __future__ import annotations


def cluster_utilization(clusters: list[dict]) -> dict:
    total_cpu_capacity = 0
    total_cpu_used = 0
    total_mem_capacity = 0
    total_mem_used = 0
    for c in clusters:
        total_cpu_capacity += c.get("cpu_capacity", 0)
        total_cpu_used += c.get("cpu_used", 0)
        total_mem_capacity += c.get("mem_capacity_gb", 0)
        total_mem_used += c.get("mem_used_gb", 0)
    cpu_pct = round(total_cpu_used / max(total_cpu_capacity, 1) * 100, 1)
    mem_pct = round(total_mem_used / max(total_mem_capacity, 1) * 100, 1)
    return {"cluster_count": len(clusters),
            "cpu": {"capacity": total_cpu_capacity, "used": total_cpu_used, "pct": cpu_pct},
            "memory": {"capacity_gb": total_mem_capacity, "used_gb": total_mem_used, "pct": mem_pct},
            "overall_health": "healthy" if cpu_pct < 70 and mem_pct < 70 else "warning" if cpu_pct < 85 else "critical"}
