"""Comparison page — full page comparing multiple apps side by side."""


def build_comparison_page(*, apps: list[dict]) -> dict:
    if len(apps) < 2 or len(apps) > 4:
        return {"error": "Compare 2-4 apps", "page": None}
    dimensions = [
        {"key": "rating", "label": "Rating", "icon": "⭐"},
        {"key": "installs", "label": "Installs", "icon": "📥"},
        {"key": "price", "label": "Price", "icon": "💰"},
        {"key": "features", "label": "Features", "icon": "✨"},
        {"key": "uptime", "label": "Uptime", "icon": "📊"},
        {"key": "support", "label": "Support", "icon": "💬"},
        {"key": "docs", "label": "Documentation", "icon": "📚"},
        {"key": "last_updated", "label": "Last Updated", "icon": "🕐"},
    ]
    rows = []
    for dim in dimensions:
        row = {"dimension": dim["label"], "icon": dim["icon"], "values": {}}
        for app in apps:
            row["values"][app["id"]] = app.get(dim["key"], "N/A")
        rows.append(row)
    # Determine winner per dimension
    for row in rows:
        vals = {k: v for k, v in row["values"].items() if isinstance(v, (int, float))}
        if vals:
            row["winner"] = max(vals, key=vals.get)
    return {
        "page_type": "app_comparison",
        "apps": [{"id": a["id"], "name": a["name"], "icon": a.get("icon")} for a in apps],
        "rows": rows, "dimension_count": len(rows), "error": None,
    }
