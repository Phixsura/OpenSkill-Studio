"""App comparison tool — side-by-side comparison of marketplace apps."""
from __future__ import annotations
import html


def compare_apps(apps: list[dict], *, features: list[str] | None = None) -> dict:
    if len(apps) < 2:
        return {"error": "Need at least 2 apps to compare"}
    all_features = features or sorted({f for a in apps for f in a.get("features", {}).keys()})
    columns = []
    for a in apps:
        feats = a.get("features", {})
        columns.append({
            "name": html.escape(a.get("name", "")),
            "icon": a.get("icon", "📱"),
            "rating": a.get("rating", 0),
            "installs": a.get("installs", 0),
            "price": a.get("price_display", "Free"),
            "feature_values": {f: feats.get(f, False) for f in all_features},
        })
    return {"columns": columns, "features": all_features,
            "app_count": len(columns), "feature_count": len(all_features)}
