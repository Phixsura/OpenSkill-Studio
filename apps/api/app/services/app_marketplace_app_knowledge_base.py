"""Knowledge base — searchable help articles for apps."""

import re


def search_articles(*, query: str, articles: list[dict], limit: int = 10) -> dict:
    if not query.strip():
        return {"results": articles[:limit], "total": len(articles), "query": ""}
    q = query.lower().strip()
    scored = []
    for a in articles:
        title_match = q in a.get("title", "").lower()
        body_match = q in a.get("body", "").lower()
        tag_match = any(q in t.lower() for t in a.get("tags", []))
        score = (title_match * 3) + (body_match * 1) + (tag_match * 2)
        if score > 0:
            scored.append({**a, "_score": score})
    scored.sort(key=lambda x: x["_score"], reverse=True)
    for s in scored:
        del s["_score"]
    return {"results": scored[:limit], "total": len(scored), "query": query}


def get_article_stats(*, articles: list[dict]) -> dict:
    total = len(articles)
    by_category: dict[str, int] = {}
    total_views = 0
    for a in articles:
        cat = a.get("category", "general")
        by_category[cat] = by_category.get(cat, 0) + 1
        total_views += a.get("views", 0)
    return {"total_articles": total, "by_category": by_category,
            "total_views": total_views,
            "avg_views": round(total_views / max(total, 1), 1)}
