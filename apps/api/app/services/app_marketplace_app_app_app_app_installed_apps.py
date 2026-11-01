"""App installed apps — user's installed apps management page."""

import html
from datetime import datetime, timezone


def build_installed_apps_page(*, apps: list[dict]) -> dict:
    items = []
    total_api_calls = 0
    for a in apps:
        api = a.get("api_calls_30d", 0)
        total_api_calls += api
        items.append({
            "id": a.get("id", ""),
            "name": html.escape(a.get("name", "")),
            "icon": a.get("icon", "📦"),
            "version": a.get("version", "1.0.0"),
            "installed_at": a.get("installed_at", ""),
            "auto_update": a.get("auto_update", True),
            "api_calls_30d": api,
            "status": a.get("status", "active"),
            "has_update": a.get("has_update", False),
            "update_version": a.get("update_version"),
        })
    updates_available = sum(1 for i in items if i["has_update"])
    return {"apps": items, "total": len(items), "total_api_calls": total_api_calls,
            "updates_available": updates_available,
            "has_updates": updates_available > 0}
