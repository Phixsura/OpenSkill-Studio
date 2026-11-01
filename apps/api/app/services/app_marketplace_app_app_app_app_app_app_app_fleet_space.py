"""Fleet SPACE framework — satisfaction, performance, activity, communication, efficiency."""
from __future__ import annotations
def fleet_space_metrics(metrics: dict) -> dict:
    dims = ["satisfaction", "performance", "activity", "communication", "efficiency"]
    scores = [metrics.get(d, 0) for d in dims]
    avg = round(sum(scores) / len(dims), 1)
    weak = [d for d, s in zip(dims, scores) if s < 60]
    return {"score": avg, "weak_dimensions": weak,
            "balanced": len(weak) == 0, "dimensions": dict(zip(dims, scores))}
