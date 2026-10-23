"""Global search — unified search across apps, developers, docs, and community."""

def global_search(*, query: str, apps: list[dict], developers: list[dict], docs: list[dict]) -> dict:
    q = query.lower()
    results = {"apps": [], "developers": [], "docs": []}
    for a in apps:
        if q in a.get("name", "").lower() or q in a.get("description", "").lower():
            results["apps"].append({"type": "app", "name": a["name"], "id": a.get("id")})
    for d in developers:
        if q in d.get("name", "").lower():
            results["developers"].append({"type": "developer", "name": d["name"]})
    for doc in docs:
        if q in doc.get("title", "").lower() or q in doc.get("content", "").lower():
            results["docs"].append({"type": "doc", "title": doc["title"]})
    total = sum(len(v) for v in results.values())
    return {"query": query, "results": results, "total": total}
