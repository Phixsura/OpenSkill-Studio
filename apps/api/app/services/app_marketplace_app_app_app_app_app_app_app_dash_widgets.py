"""Dashboard widgets — configurable widget system for developer dashboard."""
from __future__ import annotations

WIDGET_REGISTRY = {
    "api_calls": {"title": "API Calls", "icon": "📡", "size": "sm", "type": "metric"},
    "error_rate": {"title": "Error Rate", "icon": "❌", "size": "sm", "type": "metric"},
    "active_users": {"title": "Active Users", "icon": "👥", "size": "sm", "type": "metric"},
    "deploy_status": {"title": "Deploy Status", "icon": "🚀", "size": "md", "type": "status"},
    "recent_activity": {"title": "Recent Activity", "icon": "📋", "size": "lg", "type": "feed"},
    "health_check": {"title": "Health Check", "icon": "🩺", "size": "md", "type": "status"},
    "revenue": {"title": "Revenue", "icon": "💰", "size": "sm", "type": "metric"},
    "uptime": {"title": "Uptime", "icon": "🟢", "size": "sm", "type": "metric"},
}


def get_widget(widget_id: str) -> dict | None:
    w = WIDGET_REGISTRY.get(widget_id)
    return {"id": widget_id, **w} if w else None


def build_dashboard_layout(widget_ids: list[str]) -> dict:
    widgets = [{"id": wid, **WIDGET_REGISTRY[wid]} for wid in widget_ids if wid in WIDGET_REGISTRY]
    return {"widgets": widgets, "count": len(widgets),
            "layout": _compute_layout(widgets)}


def _compute_layout(widgets: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = [[]]
    row_width = 0
    sizes = {"sm": 1, "md": 2, "lg": 3}
    for w in widgets:
        s = sizes.get(w["size"], 1)
        if row_width + s > 4:
            rows.append([])
            row_width = 0
        rows[-1].append(w["id"])
        row_width += s
    return rows


def list_widgets() -> list[dict]:
    return [{"id": k, **v} for k, v in WIDGET_REGISTRY.items()]
