"""Fleet Observability Cost v9 — track monitoring and logging costs."""
from __future__ import annotations
def fleet_observability_cost_v9(sources: list[dict]) -> dict:
    total_cost = sum(s.get("monthly_cost", 0) for s in sources)
    metrics_cost = sum(s.get("metrics_cost", 0) for s in sources)
    logs_cost = sum(s.get("logs_cost", 0) for s in sources)
    traces_cost = sum(s.get("traces_cost", 0) for s in sources)
    return {"sources": len(sources), "total_monthly": round(total_cost, 2),
            "metrics_cost": round(metrics_cost, 2), "logs_cost": round(logs_cost, 2),
            "traces_cost": round(traces_cost, 2), "healthy": True}
