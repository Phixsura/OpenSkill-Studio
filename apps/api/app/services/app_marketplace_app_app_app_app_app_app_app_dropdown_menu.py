"""Dropdown menu builder — construct context menus with groups and actions."""
from __future__ import annotations
import html


def build_menu(items: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for item in items:
        group = item.get("group", "default")
        groups.setdefault(group, []).append({
            "id": item["id"], "label": html.escape(item.get("label", "")),
            "icon": item.get("icon", ""), "shortcut": item.get("shortcut", ""),
            "disabled": item.get("disabled", False),
            "danger": item.get("danger", False),
        })
    sections = [{"group": g, "items": items} for g, items in groups.items()]
    return {"sections": sections, "total_items": sum(len(s["items"]) for s in sections)}
