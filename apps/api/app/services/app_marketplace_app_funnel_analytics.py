"""Funnel analytics — track conversion funnel from view to install."""


def build_funnel(*, page_views: int, detail_views: int, install_starts: int,
                   install_completes: int) -> dict:
    steps = [
        {"step": "page_view", "count": page_views, "label": "Marketplace View"},
        {"step": "detail_view", "count": detail_views, "label": "App Detail View"},
        {"step": "install_start", "count": install_starts, "label": "Install Started"},
        {"step": "install_complete", "count": install_completes, "label": "Install Complete"},
    ]
    for i, step in enumerate(steps):
        prev = steps[i - 1]["count"] if i > 0 else step["count"]
        step["conversion_pct"] = round(step["count"] / max(prev, 1) * 100, 1)
        step["drop_off_pct"] = round(100 - step["conversion_pct"], 1) if i > 0 else 0
    overall = round(install_completes / max(page_views, 1) * 100, 2)
    return {"steps": steps, "overall_conversion": overall}


def compare_funnels(*, funnel_a: dict, funnel_b: dict) -> dict:
    comparison = []
    for sa, sb in zip(funnel_a.get("steps", []), funnel_b.get("steps", [])):
        comparison.append({
            "step": sa["step"], "a_count": sa["count"], "b_count": sb["count"],
            "a_conversion": sa["conversion_pct"], "b_conversion": sb["conversion_pct"],
            "diff": round(sb["conversion_pct"] - sa["conversion_pct"], 1),
        })
    return {"comparison": comparison,
            "overall_diff": round(funnel_b.get("overall_conversion", 0) - funnel_a.get("overall_conversion", 0), 2)}
