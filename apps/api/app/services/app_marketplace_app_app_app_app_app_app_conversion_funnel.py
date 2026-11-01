"""Conversion funnel — marketplace conversion funnel analysis."""


def build_conversion_funnel(*, steps: list[dict]) -> dict:
    items = []
    for i, s in enumerate(steps):
        count = s.get("count", 0)
        prev_count = steps[i - 1].get("count", count) if i > 0 else count
        drop_off = round((1 - count / max(prev_count, 1)) * 100, 1) if prev_count > 0 else 0
        conversion = round(count / max(steps[0].get("count", 1), 1) * 100, 1)
        items.append({
            "step": s.get("name", f"Step {i+1}"),
            "count": count, "drop_off_pct": drop_off if i > 0 else 0,
            "conversion_pct": conversion,
            "icon": s.get("icon", "📊"),
        })
    overall = items[-1]["conversion_pct"] if items else 0
    worst_idx = max(range(1, len(items)), key=lambda i: items[i]["drop_off_pct"]) if len(items) > 1 else 0
    return {"steps": items, "step_count": len(items),
            "overall_conversion": overall,
            "worst_step": items[worst_idx]["step"] if worst_idx > 0 else None}
