"""Marketplace category stats — per-category aggregate statistics."""


def compute_category_stats(apps: list[dict]) -> list[dict]:
    """Compute stats per category from a list of apps."""
    cats: dict[str, dict] = {}
    for app in apps:
        cat = app.get("category", "unknown")
        if cat not in cats:
            cats[cat] = {"category": cat, "count": 0, "installs": 0, "avg_health": 0, "health_sum": 0}
        cats[cat]["count"] += 1
        cats[cat]["installs"] += app.get("install_count", 0)
        cats[cat]["health_sum"] += app.get("health_score", 100)

    result = []
    for cat_data in cats.values():
        cat_data["avg_health"] = round(cat_data["health_sum"] / cat_data["count"], 1) if cat_data["count"] else 0
        del cat_data["health_sum"]
        result.append(cat_data)
    return sorted(result, key=lambda x: x["count"], reverse=True)
