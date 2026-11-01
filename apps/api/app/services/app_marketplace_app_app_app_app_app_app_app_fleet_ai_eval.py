"""Fleet AI Evaluation — track model evaluation pipelines."""
from __future__ import annotations
def fleet_ai_eval(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    evaluations_24h = sum(p.get("evaluations_24h", 0) for p in pipelines)
    metrics = sum(p.get("metrics_tracked", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "active": len(active), "evaluations_24h": evaluations_24h,
            "metrics": metrics, "all_active": len(active) == len(pipelines)}
