"""Performance budget tracker — enforce performance budgets."""
from __future__ import annotations


def create_budget(name: str, budgets: dict[str, float]) -> dict:
    return {"name": name, "budgets": budgets, "metric_count": len(budgets)}


def check_budget(budget: dict, actuals: dict[str, float]) -> dict:
    results = []
    violations = 0
    for metric, limit in budget["budgets"].items():
        actual = actuals.get(metric, 0)
        over = actual > limit
        if over:
            violations += 1
        results.append({"metric": metric, "limit": limit, "actual": actual,
                        "over": over, "delta": round(actual - limit, 2),
                        "pct_of_budget": round(actual / max(limit, 0.01) * 100, 1)})
    return {"name": budget["name"], "results": results, "violations": violations,
            "total": len(results), "within_budget": violations == 0}


def trend_budgets(history: list[dict]) -> dict:
    if not history:
        return {"trend": "unknown", "improving": False}
    recent = history[-1].get("violations", 0)
    prev = history[-2].get("violations", 0) if len(history) >= 2 else recent
    return {"current_violations": recent, "previous_violations": prev,
            "improving": recent < prev, "trend": "improving" if recent < prev else "worsening" if recent > prev else "stable"}
