"""App switcher — quick navigation between developer's apps."""


def build_app_switcher(*, apps: list[dict], current_app_id: str | None = None) -> dict:
    items = []
    for app in apps:
        items.append({
            "id": app["id"],
            "name": app["name"],
            "icon": app.get("icon", app["name"][0]),
            "status": app.get("status", "active"),
            "installs": app.get("installs", 0),
            "current": app["id"] == current_app_id,
        })
    items.sort(key=lambda a: (not a["current"], -a["installs"]))
    return {"apps": items, "total": len(items),
            "current_app": next((a for a in items if a["current"]), None)}
