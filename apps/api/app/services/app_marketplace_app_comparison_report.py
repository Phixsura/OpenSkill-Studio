"""Marketplace app comparison report — detailed side-by-side comparison."""


def build_comparison_report(app_a: dict, app_b: dict) -> dict:
    """Build a detailed comparison report between two marketplace apps."""
    metrics = {}
    for metric in ["install_count", "health_score", "rating", "rating_count"]:
        va, vb = app_a.get(metric, 0), app_b.get(metric, 0)
        winner = "a" if va > vb else "b" if vb > va else "tie"
        metrics[metric] = {"a": va, "b": vb, "winner": winner}
    
    perms_a = set(app_a.get("permissions", []))
    perms_b = set(app_b.get("permissions", []))
    
    return {
        "apps": {"a": {"name": app_a.get("name"), "slug": app_a.get("slug")},
                 "b": {"name": app_b.get("name"), "slug": app_b.get("slug")}},
        "metrics": metrics,
        "permissions": {"only_a": sorted(perms_a - perms_b), "only_b": sorted(perms_b - perms_a),
                        "shared": sorted(perms_a & perms_b), "a_count": len(perms_a), "b_count": len(perms_b)},
        "features": {
            "a_has_sandbox": bool(app_a.get("sandbox")),
            "b_has_sandbox": bool(app_b.get("sandbox")),
            "a_has_ui": bool(app_a.get("ui_extensions")),
            "b_has_ui": bool(app_b.get("ui_extensions")),
        },
        "recommendation": _recommend(metrics),
    }


def _recommend(metrics: dict) -> str:
    a_wins = sum(1 for m in metrics.values() if m["winner"] == "a")
    b_wins = sum(1 for m in metrics.values() if m["winner"] == "b")
    if a_wins > b_wins: return "App A leads in more metrics"
    if b_wins > a_wins: return "App B leads in more metrics"
    return "Both apps are comparable"
