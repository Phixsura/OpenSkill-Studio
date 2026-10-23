"""Developer portal search — unified search across docs, API reference, and community."""


def portal_search(*, query: str, docs: list[dict], api_ref: list[dict],
                    community: list[dict], limit: int = 10) -> dict:
    q = query.lower()
    results = []
    for d in docs:
        if q in d.get("title", "").lower() or q in d.get("content", "").lower():
            results.append({"type": "doc", "title": d["title"], "url": d.get("url", ""), "score": 10})
    for a in api_ref:
        if q in a.get("path", "").lower() or q in a.get("summary", "").lower():
            results.append({"type": "api", "title": f"{a.get('method', 'GET')} {a.get('path', '')}", "url": a.get("url", ""), "score": 8})
    for c in community:
        if q in c.get("title", "").lower():
            results.append({"type": "community", "title": c["title"], "url": c.get("url", ""), "score": 5})
    results.sort(key=lambda r: -r["score"])
    return {"query": query, "results": results[:limit], "total": len(results),
            "by_type": {"doc": sum(1 for r in results if r["type"] == "doc"),
                         "api": sum(1 for r in results if r["type"] == "api"),
                         "community": sum(1 for r in results if r["type"] == "community")}}
