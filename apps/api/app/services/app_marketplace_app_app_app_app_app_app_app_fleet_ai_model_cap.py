"""Fleet AI Model Capacity — track per-model throughput capacity."""
from __future__ import annotations
def fleet_ai_model_capacity(planners: list[dict]) -> dict:
    active = [p for p in planners if p.get("active", True)]
    models = sum(p.get("models", 0) for p in planners)
    total_rps = sum(p.get("max_rps", 0) for p in planners)
    utilization = round(sum(p.get("util_pct", 0) for p in planners) / max(len(planners), 1), 1)
    return {"planners": len(planners), "active": len(active), "models": models,
            "max_rps": total_rps, "utilization": utilization, "headroom": utilization < 80}
