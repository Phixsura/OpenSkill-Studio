"""Fleet AI Distributed Training v2 — track multi-node training at scale."""
from __future__ import annotations
def fleet_ai_distributed_training_v2(trainers: list[dict]) -> dict:
    active = [t for t in trainers if t.get("active", True)]
    nodes = sum(t.get("nodes", 0) for t in trainers)
    gpus = sum(t.get("gpus", 0) for t in trainers)
    scaling_efficiency = round(sum(t.get("efficiency_pct", 0) for t in trainers) / max(len(trainers), 1), 1)
    return {"trainers": len(trainers), "active": len(active), "nodes": nodes,
            "gpus": gpus, "efficiency": scaling_efficiency, "scalable": scaling_efficiency > 80}
