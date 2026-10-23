"""Feature comparison — compare multiple apps side by side."""

import html


def compare_apps(*, apps: list[dict], features: list[str]) -> dict:
    matrix = []
    for feat in features:
        row = {"feature": html.escape(feat), "values": {}}
        for app in apps:
            app_feats = app.get("features", {})
            val = app_feats.get(feat)
            if isinstance(val, bool):
                row["values"][app["id"]] = {"value": val, "display": "✓" if val else "✗", "type": "bool"}
            elif val is not None:
                row["values"][app["id"]] = {"value": val, "display": html.escape(str(val)), "type": "text"}
            else:
                row["values"][app["id"]] = {"value": None, "display": "—", "type": "null"}
        matrix.append(row)
    columns = [{"id": a["id"], "name": html.escape(a.get("name", "")),
                "icon": a.get("icon", "📦")} for a in apps]
    return {"columns": columns, "rows": matrix,
            "app_count": len(apps), "feature_count": len(features)}
