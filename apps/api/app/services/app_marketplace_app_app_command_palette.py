"""Command palette — searchable keyboard-driven command menu."""

import html


def build_command_palette(*, commands: list[dict], query: str = "") -> dict:
    q = query.lower().strip()
    results = []
    for cmd in commands:
        label = cmd.get("label", "")
        if q and q not in label.lower() and q not in cmd.get("category", "").lower():
            continue
        results.append({
            "id": cmd.get("id", ""),
            "label": html.escape(label),
            "shortcut": cmd.get("shortcut"),
            "icon": cmd.get("icon", "⚡"),
            "category": cmd.get("category", "General"),
        })
    return {"results": results, "total": len(results), "query": q}
