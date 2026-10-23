"""Global search engine — unified search across apps, docs, users, and settings."""
from __future__ import annotations
import html
import re


def search(query: str, *, sources: list[dict], limit: int = 20) -> dict:
    if not query.strip():
        return {"results": [], "total": 0, "query": ""}
    q = query.strip().lower()
    safe_query = html.escape(query)
    results = []
    for item in sources:
        title = item.get("title", "")
        description = item.get("description", "")
        content = f"{title} {description}".lower()
        if q in content:
            # Simple relevance: title match > description match
            score = 10 if q in title.lower() else 5
            score += len(q) / max(len(content), 1) * 10  # length ratio bonus
            results.append({
                "title": html.escape(title), "description": html.escape(description[:200]),
                "type": item.get("type", "page"), "url": item.get("url", ""),
                "icon": item.get("icon", "📄"), "score": round(score, 2),
            })
    results.sort(key=lambda r: -r["score"])
    total = len(results)
    return {"results": results[:limit], "total": total, "query": safe_query,
            "shown": min(total, limit), "has_more": total > limit}
