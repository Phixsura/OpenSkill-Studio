"""Container orchestration scheduler — schedule containers across nodes."""
from __future__ import annotations


def schedule_container(container: dict, nodes: list[dict]) -> dict:
    cpu_req = container.get("cpu", 1)
    mem_req = container.get("memory_mb", 512)
    candidates = []
    for node in nodes:
        cpu_avail = node["cpu_total"] - node.get("cpu_used", 0)
        mem_avail = node["memory_mb_total"] - node.get("memory_mb_used", 0)
        if cpu_avail >= cpu_req and mem_avail >= mem_req:
            score = cpu_avail + mem_avail / 1024
            candidates.append({**node, "score": round(score, 2),
                                "cpu_avail": cpu_avail, "mem_avail": mem_avail})
    if not candidates:
        return {"scheduled": False, "reason": "no_suitable_node"}
    best = max(candidates, key=lambda n: n["score"])
    return {"scheduled": True, "node": best["name"], "score": best["score"],
            "container": container.get("name", "unnamed")}


def cluster_utilization(nodes: list[dict]) -> dict:
    total_cpu = sum(n["cpu_total"] for n in nodes)
    used_cpu = sum(n.get("cpu_used", 0) for n in nodes)
    total_mem = sum(n["memory_mb_total"] for n in nodes)
    used_mem = sum(n.get("memory_mb_used", 0) for n in nodes)
    return {"nodes": len(nodes),
            "cpu_pct": round(used_cpu / max(total_cpu, 1) * 100, 1),
            "memory_pct": round(used_mem / max(total_mem, 1) * 100, 1),
            "cpu_available": total_cpu - used_cpu,
            "memory_available_mb": total_mem - used_mem}
