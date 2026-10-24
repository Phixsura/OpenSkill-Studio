"""App list page — developer's app management list."""

import html


def build_app_list_page(*, apps: list[dict], sort_by: str = "newest") -> dict:
    sorted_apps = list(apps)
    if sort_by == "newest":
        sorted_apps.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    elif sort_by == "installs":
        sorted_apps.sort(key=lambda a: a.get("installs", 0), reverse=True)
    elif sort_by == "name":
        sorted_apps.sort(key=lambda a: a.get("name", "").lower())
    items = [{
        "id": a.get("id", ""), "name": html.escape(a.get("name", "")),
        "icon": a.get("icon", "📦"), "version": a.get("version", "1.0.0"),
        "status": a.get("status", "draft"), "installs": a.get("installs", 0),
        "rating": a.get("rating", 0), "created_at": a.get("created_at", ""),
    } for a in sorted_apps]
    status_counts = {}
    for a in items:
        s = a["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    return {"apps": items, "total": len(items), "sort_by": sort_by,
            "status_counts": status_counts,
            "has_draft": status_counts.get("draft", 0) > 0}
