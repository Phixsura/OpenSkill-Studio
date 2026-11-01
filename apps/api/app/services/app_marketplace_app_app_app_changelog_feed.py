"""App changelog feed — aggregate changelog across all installed apps."""

import html
from datetime import datetime, timezone


def build_changelog_feed(*, apps_changelogs: list[dict], limit: int = 20) -> dict:
    all_entries = []
    for ac in apps_changelogs:
        app_name = html.escape(ac.get("app_name", ""))
        app_icon = ac.get("app_icon", "📦")
        for entry in ac.get("entries", []):
            all_entries.append({
                "app_name": app_name, "app_icon": app_icon,
                "version": entry.get("version", ""),
                "title": html.escape(entry.get("title", "")),
                "type": entry.get("type", "changed"),
                "date": entry.get("date", ""),
            })
    all_entries.sort(key=lambda x: x["date"], reverse=True)
    page = all_entries[:limit]
    apps_with_updates = len(set(e["app_name"] for e in page))
    return {"entries": page, "total": len(all_entries), "shown": len(page),
            "apps_with_updates": apps_with_updates}
