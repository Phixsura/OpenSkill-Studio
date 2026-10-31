"""Help center search — search help articles with relevance scoring."""
from __future__ import annotations
import html


def search_help(query: str, articles: list[dict], *, limit: int = 10) -> dict:
    if not query.strip():
        return {"results": [], "total": 0, "query": ""}
    q = query.strip().lower()
    scored = []
    for a in articles:
        title = a.get("title", "")
        body = a.get("body", "")
        score = 0
        if q in title.lower():
            score += 10
        if q in body.lower():
            score += 5
        for tag in a.get("tags", []):
            if q in tag.lower():
                score += 3
        if score > 0:
            scored.append({
                "title": html.escape(title), "snippet": html.escape(body[:150]),
                "url": a.get("url", ""), "category": a.get("category", ""),
                "score": score,
            })
    scored.sort(key=lambda x: -x["score"])
    return {"results": scored[:limit], "total": len(scored), "query": html.escape(query),
            "shown": min(len(scored), limit)}


def get_popular_articles(articles: list[dict], *, limit: int = 5) -> list[dict]:
    ranked = sorted(articles, key=lambda a: -a.get("views", 0))[:limit]
    return [{"title": html.escape(a.get("title", "")), "url": a.get("url", ""),
             "views": a.get("views", 0)} for a in ranked]
