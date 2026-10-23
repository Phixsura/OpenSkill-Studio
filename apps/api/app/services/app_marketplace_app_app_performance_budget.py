"""Performance budget — web performance budget checker."""

import html

DEFAULTS = {
    "js_kb": 200, "css_kb": 50, "image_kb": 500, "font_kb": 100,
    "total_kb": 1000, "requests": 50, "lcp_ms": 2500, "fid_ms": 100, "cls": 0.1,
}


def check_budget(*, metrics: dict, budget: dict | None = None) -> dict:
    b = budget or DEFAULTS
    results = []
    violations = 0
    for key, limit in b.items():
        actual = metrics.get(key)
        if actual is None:
            continue
        over = actual > limit
        if over:
            violations += 1
        results.append({
            "metric": key, "limit": limit, "actual": actual,
            "over": over, "pct_of_budget": round(actual / max(limit, 0.001) * 100, 1),
        })
    return {"results": results, "total_checks": len(results), "violations": violations,
            "within_budget": violations == 0}


def summarize_budget(*, metrics: dict) -> dict:
    total_kb = sum(v for k, v in metrics.items() if k.endswith("_kb"))
    return {"total_transfer_kb": round(total_kb, 1),
            "total_transfer_display": f"{total_kb:.0f}KB" if total_kb < 1024 else f"{total_kb/1024:.1f}MB"}
