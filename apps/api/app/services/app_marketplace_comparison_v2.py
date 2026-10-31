"""App comparison v2 — detailed side-by-side comparison with scoring."""


def compare_apps_v2(*, apps: list[dict]) -> dict:
    if len(apps) < 2:
        return {"error": "Need at least 2 apps", "comparison": None}
    dimensions = ["rating", "installs", "price", "features", "support", "docs"]
    rows = []
    for dim in dimensions:
        row = {"dimension": dim}
        for app in apps:
            if dim == "rating":
                row[app["id"]] = app.get("avg_rating", 0)
            elif dim == "installs":
                row[app["id"]] = app.get("install_count", 0)
            elif dim == "price":
                row[app["id"]] = app.get("price_label", "Free")
            elif dim == "features":
                row[app["id"]] = len(app.get("features", []))
            elif dim == "support":
                row[app["id"]] = app.get("support_level", "community")
            elif dim == "docs":
                row[app["id"]] = "Yes" if app.get("has_docs") else "No"
        rows.append(row)
    # Score each app
    scores = {}
    for app in apps:
        score = app.get("avg_rating", 0) * 20 + min(100, app.get("install_count", 0) / 100)
        scores[app["id"]] = round(score, 1)
    winner = max(scores, key=scores.get) if scores else None
    return {"apps": [{"id": a["id"], "name": a["name"]} for a in apps],
            "rows": rows, "scores": scores, "winner": winner}
