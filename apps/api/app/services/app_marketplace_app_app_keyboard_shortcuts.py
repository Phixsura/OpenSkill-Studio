"""Keyboard shortcuts — context-aware shortcut binding system."""

import html

CONTEXTS = {"global", "editor", "modal", "search", "navigation"}


def register_shortcuts(*, shortcuts: list[dict]) -> dict:
    items = []
    conflicts = []
    seen: dict[str, str] = {}
    for s in shortcuts:
        combo = s.get("combo", "")
        ctx = s.get("context", "global")
        key = f"{ctx}:{combo}"
        if key in seen:
            conflicts.append({"combo": combo, "context": ctx,
                              "actions": [seen[key], html.escape(s.get("action", ""))]})
        else:
            seen[key] = html.escape(s.get("action", ""))
        items.append({"combo": combo, "action": html.escape(s.get("action", "")),
                       "context": ctx, "description": html.escape(s.get("description", "")),
                       "enabled": s.get("enabled", True)})
    by_context: dict[str, list] = {}
    for i in items:
        by_context.setdefault(i["context"], []).append(i)
    return {"shortcuts": items, "total": len(items), "conflicts": conflicts,
            "by_context": by_context, "context_count": len(by_context)}
