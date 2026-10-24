"""App comparison picker — select apps for side-by-side comparison."""
from __future__ import annotations
import html


def build_compare_selection(selected_apps: list[dict], *, max_compare: int = 4) -> dict:
    items = [{"id": a["id"], "name": html.escape(a.get("name", "")),
              "icon": a.get("icon", "📱"), "rating": a.get("rating", 0)}
             for a in selected_apps[:max_compare]]
    can_add = len(items) < max_compare
    can_compare = len(items) >= 2
    return {"selected": items, "count": len(items), "max": max_compare,
            "can_add": can_add, "can_compare": can_compare}


def find_similar_apps(app: dict, all_apps: list[dict], *, limit: int = 4) -> list[dict]:
    category = app.get("category", "")
    similar = [a for a in all_apps if a.get("category") == category and a.get("id") != app.get("id")]
    similar.sort(key=lambda a: -a.get("rating", 0))
    return similar[:limit]
