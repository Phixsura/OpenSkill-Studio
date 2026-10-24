"""Resource utilization heatmap — generate heatmap data from resource usage."""
from __future__ import annotations

def generate_heatmap(nodes: list[dict]) -> dict:
    cells = []
    for node in nodes:
        cpu = node.get("cpu_pct", 0)
        mem = node.get("memory_pct", 0)
        color = "green" if max(cpu, mem) < 60 else ("yellow" if max(cpu, mem) < 80 else "red")
        cells.append({"node": node["name"], "cpu_pct": cpu, "memory_pct": mem, "color": color})
    hot = sum(1 for c in cells if c["color"] == "red")
    return {"cells": cells, "total_nodes": len(cells), "hot_nodes": hot,
            "avg_cpu": round(sum(c["cpu_pct"] for c in cells) / max(len(cells), 1), 1)}
