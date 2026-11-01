"""Tab navigator — build tabbed navigation with badges and active state."""
from __future__ import annotations


def build_tabs(tabs: list[dict], *, active: str = "") -> dict:
    items = []
    for t in tabs:
        tid = t["id"]
        items.append({
            "id": tid, "label": t.get("label", tid),
            "icon": t.get("icon", ""), "badge": t.get("badge"),
            "active": tid == active, "disabled": t.get("disabled", False),
        })
    if not any(i["active"] for i in items) and items:
        items[0]["active"] = True
    return {"tabs": items, "active": active or (items[0]["id"] if items else ""),
            "count": len(items)}
