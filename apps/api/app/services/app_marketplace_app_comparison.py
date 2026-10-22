"""App comparison — side-by-side feature matrix for marketplace."""


def compare_apps(apps: list[dict]) -> dict:
    if len(apps) < 2:
        return {"error": "Need at least 2 apps to compare", "comparison": None}
    features = set()
    for app in apps:
        features.update(app.get("features", []))
    matrix = []
    for feat in sorted(features):
        row = {"feature": feat}
        for app in apps:
            row[app["id"]] = feat in app.get("features", [])
        matrix.append(row)
    return {
        "apps": [{"id": a["id"], "name": a["name"], "category": a.get("category")} for a in apps],
        "matrix": matrix,
        "total_features": len(features),
        "common_features": sum(1 for row in matrix if all(row.get(a["id"]) for a in apps)),
    }
