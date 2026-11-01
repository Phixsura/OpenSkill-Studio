"""Fleet health aggregator — weighted health across all dimensions."""
from __future__ import annotations
def fleet_health_aggregator(dimensions: list[dict]) -> dict:
    total_weight = sum(d.get("weight", 1) for d in dimensions)
    weighted_score = sum(d.get("score", 0) * d.get("weight", 1) for d in dimensions)
    overall = round(weighted_score / max(total_weight, 1), 1)
    critical = [d for d in dimensions if d.get("score", 100) < 50]
    return {"overall_score": overall, "dimensions": len(dimensions),
            "critical": len(critical), "status": "healthy" if overall >= 80 else ("degraded" if overall >= 60 else "critical")}
