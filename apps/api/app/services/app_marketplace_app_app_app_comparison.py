"""App comparison — side-by-side app metrics comparison."""

import html


def compare_apps_metrics(*, apps: list[dict]) -> dict:
    metrics = ["rating", "downloads", "review_count", "response_time_ms", "uptime_pct"]
    comparison = []
    for metric in metrics:
        values = {}
        for app in apps:
            values[app["id"]] = app.get(metric, 0)
        best_id = max(values, key=values.get) if values else None
        comparison.append({"metric": metric, "label": metric.replace("_", " ").title(),
                            "values": values, "best": best_id})
    columns = [{"id": a["id"], "name": html.escape(a.get("name", "")),
                "icon": a.get("icon", "📦")} for a in apps]
    return {"columns": columns, "comparison": comparison,
            "app_count": len(apps), "metric_count": len(comparison)}
