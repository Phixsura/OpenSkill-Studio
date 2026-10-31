"""Hotkey manager — keyboard shortcut registry and conflict detection."""

import html


def build_hotkey_registry(*, shortcuts: list[dict]) -> dict:
    items = []
    key_map: dict[str, str] = {}
    conflicts = []
    for s in shortcuts:
        combo = s.get("combo", "").strip()
        action = html.escape(s.get("action", ""))
        if combo in key_map:
            conflicts.append({"combo": combo, "actions": [key_map[combo], action]})
        else:
            key_map[combo] = action
        items.append({"combo": combo, "action": action,
                       "category": s.get("category", "General"),
                       "enabled": s.get("enabled", True)})
    categories = sorted(set(i["category"] for i in items))
    return {"shortcuts": items, "total": len(items), "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0, "categories": categories}
