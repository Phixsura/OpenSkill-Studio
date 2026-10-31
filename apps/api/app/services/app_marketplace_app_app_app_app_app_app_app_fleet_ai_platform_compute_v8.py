"""Fleet AI Compute v8 — track ultimate AI compute orchestration."""
from __future__ import annotations
def fleet_ai_compute_v8(clusters: list[dict]) -> dict:
    active = [c for c in clusters if c.get("active", True)]
    nodes = sum(c.get("nodes", 0) for c in clusters)
    gpus = sum(c.get("gpus", 0) for c in clusters)
    tflops = sum(c.get("tflops", 0) for c in clusters)
    utilization = round(sum(c.get("util_pct", 0) for c in clusters) / max(len(clusters), 1), 1)
    return {"clusters": len(clusters), "active": len(active), "nodes": nodes,
            "gpus": gpus, "tflops": tflops, "utilization": utilization, "efficient": utilization > 80}
