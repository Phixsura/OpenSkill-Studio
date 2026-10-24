"""Dashboard widget — configurable widgets for developer dashboards."""

import secrets


WIDGET_TYPES = {
    "metric_card": {"label": "Metric Card", "min_w": 1, "min_h": 1, "icon": "📊"},
    "chart": {"label": "Chart", "min_w": 2, "min_h": 2, "icon": "📈"},
    "table": {"label": "Data Table", "min_w": 2, "min_h": 2, "icon": "📋"},
    "alert_feed": {"label": "Alert Feed", "min_w": 1, "min_h": 2, "icon": "🔔"},
    "status_grid": {"label": "Status Grid", "min_w": 2, "min_h": 1, "icon": "🟢"},
    "quick_actions": {"label": "Quick Actions", "min_w": 1, "min_h": 1, "icon": "⚡"},
}


def create_widget(*, widget_type: str, title: str, config: dict | None = None,
                    position: dict | None = None) -> dict:
    wt = WIDGET_TYPES.get(widget_type)
    if not wt:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(WIDGET_TYPES))}"}
    pos = position or {"x": 0, "y": 0, "w": wt["min_w"], "h": wt["min_h"]}
    return {
        "widget_id": f"wgt_{secrets.token_urlsafe(6)}",
        "type": widget_type,
        "type_info": wt,
        "title": title,
        "config": config or {},
        "position": pos,
    }


def build_dashboard_layout(*, widgets: list[dict], columns: int = 4) -> dict:
    return {
        "widgets": widgets,
        "total_widgets": len(widgets),
        "columns": columns,
        "types_used": list(set(w.get("type", "") for w in widgets)),
    }
