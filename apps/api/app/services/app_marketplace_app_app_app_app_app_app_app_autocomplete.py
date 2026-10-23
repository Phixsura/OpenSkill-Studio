"""Search autocomplete — prefix-based suggestions for marketplace search."""
from __future__ import annotations
import html


def build_suggestions(query: str, *, apps: list[str], categories: list[str],
                        developers: list[str], limit: int = 8) -> dict:
    q = query.strip().lower()
    if not q:
        return {"suggestions": [], "query": ""}
    results = []
    for name in apps:
        if q in name.lower():
            results.append({"text": html.escape(name), "type": "app", "icon": "📱"})
    for cat in categories:
        if q in cat.lower():
            results.append({"text": html.escape(cat), "type": "category", "icon": "📦"})
    for dev in developers:
        if q in dev.lower():
            results.append({"text": html.escape(dev), "type": "developer", "icon": "👩‍💻"})
    return {"suggestions": results[:limit], "query": html.escape(query),
            "total": len(results), "shown": min(len(results), limit)}
