"""Developer portal search — search across apps, docs, events, and settings."""


def portal_search(query: str, *, apps: list[dict] | None = None, docs: list[dict] | None = None) -> dict:
    q = query.lower().strip()
    if not q:
        return {"results": [], "total": 0}
    
    results = []
    for app in (apps or []):
        if q in app.get("name", "").lower() or q in app.get("slug", "").lower():
            results.append({"type": "app", "title": app["name"], "url": f"/dashboard/developer/apps/{app.get('id', '')}"})
    for doc in (docs or []):
        if q in doc.get("title", "").lower():
            results.append({"type": "doc", "title": doc["title"], "url": doc.get("url", "")})
    
    return {"results": results[:20], "total": len(results), "query": q}
