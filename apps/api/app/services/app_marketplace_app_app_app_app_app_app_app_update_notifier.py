"""App update notifier — check for and notify about available app updates."""
from __future__ import annotations


def check_updates(installed_apps: list[dict]) -> dict:
    updates = []
    for app in installed_apps:
        current = app.get("installed_version", "")
        latest = app.get("latest_version", current)
        if current and latest and current != latest:
            updates.append({
                "name": app["name"], "icon": app.get("icon", "📱"),
                "current": current, "latest": latest,
                "changelog": app.get("changelog", ""),
                "breaking": app.get("breaking", False),
            })
    return {"updates": updates, "count": len(updates),
            "has_breaking": any(u["breaking"] for u in updates),
            "all_current": len(updates) == 0}


def build_update_summary(updates: list[dict]) -> str:
    if not updates:
        return "All apps are up to date! ✅"
    breaking = sum(1 for u in updates if u["breaking"])
    msg = f"{len(updates)} update{'s' if len(updates) > 1 else ''} available"
    if breaking:
        msg += f" ({breaking} breaking)"
    return msg
