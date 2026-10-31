"""App search bar — unified search with autocomplete suggestions."""

import html
from collections import defaultdict


def get_suggestions(*, query: str, apps: list[dict], docs: list[dict] | None = None,
                      max_per_section: int = 3) -> dict:
    q = query.lower().strip()
    if not q or len(q) < 2:
        return {"suggestions": [], "total": 0, "query": query}
    sections: dict[str, list] = {}
    app_matches = [{"label": html.escape(a.get("name", "")), "icon": a.get("icon", "📦"),
                     "type": "app", "href": f"/apps/{a.get('id', '')}"}
                    for a in apps if q in a.get("name", "").lower()][:max_per_section]
    if app_matches:
        sections["Apps"] = app_matches
    if docs:
        doc_matches = [{"label": html.escape(d.get("title", "")), "icon": "📝",
                         "type": "doc", "href": d.get("path", "")}
                        for d in docs if q in d.get("title", "").lower()][:max_per_section]
        if doc_matches:
            sections["Docs"] = doc_matches
    all_items = [item for items in sections.values() for item in items]
    return {"suggestions": all_items, "sections": sections,
            "total": len(all_items), "query": query}
