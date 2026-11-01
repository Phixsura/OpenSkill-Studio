"""Analytics funnel — track user journey through marketplace funnels."""
from __future__ import annotations


def build_funnel(steps: list[dict]) -> dict:
    results = []
    prev_count = steps[0]["count"] if steps else 0
    for i, step in enumerate(steps):
        count = step["count"]
        drop_off = prev_count - count if i > 0 else 0
        drop_pct = round(drop_off / max(prev_count, 1) * 100, 1) if i > 0 else 0
        conversion = round(count / max(steps[0]["count"], 1) * 100, 1)
        results.append({
            "step": step["name"], "count": count,
            "drop_off": drop_off, "drop_pct": drop_pct,
            "conversion": conversion,
            "conversion_display": f"{conversion}%",
        })
        prev_count = count
    overall = round(steps[-1]["count"] / max(steps[0]["count"], 1) * 100, 1) if steps else 0
    worst_step = max(results[1:], key=lambda r: r["drop_pct"]) if len(results) > 1 else None
    return {"steps": results, "overall_conversion": overall,
            "overall_display": f"{overall}%",
            "worst_step": worst_step["step"] if worst_step else None,
            "total_steps": len(results)}
