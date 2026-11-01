"""Fleet AI Compute v4 — track AI platform compute orchestration."""
from __future__ import annotations
def fleet_ai_compute_v4(clusters: list[dict]) -> dict:
    active = [c for c in clusters if c.get("active", True)]
    nodes = sum(c.get("nodes", 0) for c in clusters)
    gpus = sum(c.get("gpus", 0) for c in clusters)
    tflops = sum(c.get("tflops", 0) for c in clusters)
    return {"clusters": len(clusters), "active": len(active), "nodes": nodes,
            "gpus": gpus, "tflops": tflops, "powerful": tflops > 100000}
