"""Cluster node monitor — track node health in compute clusters."""
from __future__ import annotations


def create_node(name: str, cpu_cores: int, memory_gb: int, zone: str,
                 cpu_used_pct: float = 0, memory_used_pct: float = 0) -> dict:
    status = "ready"
    if cpu_used_pct > 90 or memory_used_pct > 90:
        status = "pressure"
    return {"name": name, "cpu_cores": cpu_cores, "memory_gb": memory_gb,
            "zone": zone, "cpu_used_pct": cpu_used_pct,
            "memory_used_pct": memory_used_pct, "status": status,
            "pods": 0}


def cluster_summary(nodes: list[dict]) -> dict:
    total_cpu = sum(n["cpu_cores"] for n in nodes)
    total_mem = sum(n["memory_gb"] for n in nodes)
    avg_cpu = round(sum(n["cpu_used_pct"] for n in nodes) / max(len(nodes), 1), 1)
    avg_mem = round(sum(n["memory_used_pct"] for n in nodes) / max(len(nodes), 1), 1)
    by_zone: dict[str, int] = {}
    for n in nodes:
        by_zone[n["zone"]] = by_zone.get(n["zone"], 0) + 1
    ready = sum(1 for n in nodes if n["status"] == "ready")
    return {"node_count": len(nodes), "ready": ready, "pressure": len(nodes) - ready,
            "total_cpu_cores": total_cpu, "total_memory_gb": total_mem,
            "avg_cpu_pct": avg_cpu, "avg_memory_pct": avg_mem, "by_zone": by_zone}
