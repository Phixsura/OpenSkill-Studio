"""Global search — unified search across apps, docs, and users."""

import html


def global_search(*, query: str, apps: list[dict] | None = None,
                    docs: list[dict] | None = None, users: list[dict] | None = None) -> dict:
    q = query.lower().strip()
    if not q:
        return {"results": [], "total": 0, "query": query, "sections": {}}
    sections: dict[str, list] = {}
    if apps:
        matched = [{"type": "app", "title": html.escape(a.get("name", "")),
                      "subtitle": html.escape(a.get("description", "")[:80]),
                      "icon": a.get("icon", "📦"), "href": f"/apps/{a.get('id', '')}"}
                     for a in apps if q in a.get("name", "").lower() or q in a.get("description", "").lower()]
        if matched:
            sections["Apps"] = matched[:5]
    if docs:
        matched = [{"type": "doc", "title": html.escape(d.get("title", "")),
                      "subtitle": html.escape(d.get("path", "")),
                      "icon": "📝", "href": d.get("path", "")}
                     for d in docs if q in d.get("title", "").lower()]
        if matched:
            sections["Docs"] = matched[:5]
    if users:
        matched = [{"type": "user", "title": html.escape(u.get("name", "")),
                      "subtitle": html.escape(u.get("email", "")),
                      "icon": "👤", "href": f"/users/{u.get('id', '')}"}
                     for u in users if q in u.get("name", "").lower()]
        if matched:
            sections["Users"] = matched[:5]
    total = sum(len(v) for v in sections.values())
    return {"results": [item for items in sections.values() for item in items],
            "total": total, "query": query, "sections": sections}
