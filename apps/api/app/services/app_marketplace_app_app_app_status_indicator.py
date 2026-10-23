"""App status indicator — real-time app status display."""

import html
from datetime import datetime, timezone

STATUSES = {
    "online": {"label": "Online", "icon": "🟢", "color": "green"},
    "offline": {"label": "Offline", "icon": "🔴", "color": "red"},
    "maintenance": {"label": "Maintenance", "icon": "🔵", "color": "blue"},
    "degraded": {"label": "Degraded", "icon": "🟡", "color": "yellow"},
    "deploying": {"label": "Deploying", "icon": "🟠", "color": "orange"},
}


def get_status_indicator(*, status: str, app_name: str = "",
                           last_checked: str | None = None) -> dict:
    info = STATUSES.get(status, STATUSES["offline"])
    return {
        "status": status, "label": info["label"], "icon": info["icon"],
        "color": info["color"], "app_name": html.escape(app_name),
        "last_checked": last_checked or datetime.now(timezone.utc).isoformat(),
        "is_healthy": status in ("online",),
    }


def build_status_grid(*, apps: list[dict]) -> dict:
    items = [get_status_indicator(status=a.get("status", "online"),
                                    app_name=a.get("name", ""))
             for a in apps]
    online = sum(1 for i in items if i["is_healthy"])
    return {"apps": items, "total": len(items), "online": online,
            "offline": len(items) - online,
            "overall": "healthy" if online == len(items) else "degraded"}
