"""App conversion funnel — track visitor to install conversion."""


def build_conversion_funnel(*, steps: list[dict]) -> dict:
    if not steps:
        return {"steps": [], "overall_conversion": 0}
    top = steps[0].get("count", 0)
    enriched = []
    for i, step in enumerate(steps):
        count = step.get("count", 0)
        pct_of_total = round(count / max(top, 1) * 100, 1)
        drop_off = steps[i - 1].get("count", top) - count if i > 0 else 0
        drop_pct = round(drop_off / max(steps[i - 1].get("count", top), 1) * 100, 1) if i > 0 else 0
        enriched.append({
            "name": step["name"],
            "count": count,
            "pct_of_total": pct_of_total,
            "drop_off": drop_off,
            "drop_off_pct": drop_pct,
        })
    overall = round(enriched[-1]["count"] / max(top, 1) * 100, 1)
    worst_drop = max(enriched[1:], key=lambda s: s["drop_off_pct"]) if len(enriched) > 1 else None
    return {
        "steps": enriched,
        "overall_conversion": overall,
        "worst_step": worst_drop["name"] if worst_drop and worst_drop["drop_off_pct"] > 0 else None,
    }
