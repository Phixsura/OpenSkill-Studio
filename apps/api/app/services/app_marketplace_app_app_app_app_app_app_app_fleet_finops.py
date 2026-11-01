"""Fleet FinOps — cloud financial operations maturity."""
from __future__ import annotations
def fleet_finops_score(metrics: dict) -> dict:
    visibility = metrics.get("cost_visibility_pct", 0)
    optimization = metrics.get("optimization_pct", 0)
    governance = metrics.get("governance_pct", 0)
    score = round((visibility + optimization + governance) / 3, 1)
    level = "Run" if score >= 80 else ("Walk" if score >= 50 else "Crawl")
    return {"score": score, "level": level, "visibility": visibility,
            "optimization": optimization, "governance": governance}
