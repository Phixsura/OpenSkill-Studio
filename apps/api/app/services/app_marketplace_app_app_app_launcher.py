"""App launcher — quick-launch grid for installed apps."""

import html


def build_launcher(*, apps: list[dict], pinned: list[str] | None = None,
                     recent_limit: int = 8) -> dict:
    pin_set = set(pinned or [])
    pinned_apps = [a for a in apps if a.get("id") in pin_set]
    recent = [a for a in apps if a.get("id") not in pin_set][:recent_limit]
    items = []
    for a in pinned_apps + recent:
        items.append({
            "id": a.get("id", ""),
            "name": html.escape(a.get("name", "")),
            "icon": a.get("icon", "📦"),
            "url": a.get("url", "#"),
            "pinned": a.get("id") in pin_set,
            "category": a.get("category", ""),
        })
    return {"apps": items, "total": len(items),
            "pinned_count": len(pinned_apps), "recent_count": len(recent)}
