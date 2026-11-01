"""Workload distribution analyzer — analyze workload balance across nodes."""
from __future__ import annotations
import math


def analyze_distribution(nodes: list[dict]) -> dict:
    loads = [n.get("load_pct", 0) for n in nodes]
    if not loads:
        return {"balanced": True, "nodes": 0}
    avg = round(sum(loads) / len(loads), 1)
    std = round(math.sqrt(sum((l - avg) ** 2 for l in loads) / len(loads)), 1)
    max_load = max(loads)
    min_load = min(loads)
    spread = max_load - min_load
    balanced = std < 15 and spread < 30
    hotspot = next((n["name"] for n in nodes if n.get("load_pct", 0) == max_load), None)
    return {"nodes": len(nodes), "avg_load": avg, "std": std,
            "max_load": max_load, "min_load": min_load, "spread": spread,
            "balanced": balanced, "hotspot": hotspot}
