"""Performance budget — set and enforce performance budgets."""


DEFAULT_BUDGETS = {
    "js_size_kb": 300,
    "css_size_kb": 100,
    "image_size_kb": 500,
    "total_size_kb": 1000,
    "first_paint_ms": 1500,
    "fcp_ms": 2000,
    "lcp_ms": 2500,
    "tti_ms": 3500,
    "cls": 0.1,
}


def check_budget(*, budgets: dict | None = None, actuals: dict) -> dict:
    limits = {**DEFAULT_BUDGETS, **(budgets or {})}
    results = []
    for key, limit in limits.items():
        actual = actuals.get(key)
        if actual is None:
            continue
        over = actual > limit
        pct = round(actual / max(limit, 0.001) * 100, 1)
        results.append({
            "metric": key,
            "budget": limit,
            "actual": actual,
            "over_budget": over,
            "usage_pct": pct,
            "overage": round(actual - limit, 3) if over else 0,
        })
    violations = [r for r in results if r["over_budget"]]
    return {
        "results": results,
        "total_metrics": len(results),
        "violations": len(violations),
        "passing": len(results) - len(violations),
        "all_within_budget": len(violations) == 0,
    }
