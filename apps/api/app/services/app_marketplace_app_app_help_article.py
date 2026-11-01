"""Help article — structured help content for the knowledge base."""

import html
import re


def create_help_article(*, title: str, body: str, category: str,
                          tags: list[str], author: str) -> dict:
    safe_title = html.escape(title)
    word_count = len(body.split())
    read_time = max(word_count // 200, 1)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return {
        "slug": slug,
        "title": safe_title,
        "body": body,
        "category": category,
        "tags": tags,
        "author": author,
        "word_count": word_count,
        "read_time_min": read_time,
        "url": f"/help/{category}/{slug}",
    }


def search_help(*, query: str, articles: list[dict], limit: int = 5) -> dict:
    q = query.lower()
    results = []
    for a in articles:
        score = 0
        if q in a.get("title", "").lower():
            score += 10
        if q in a.get("body", "").lower():
            score += 3
        if any(q in t.lower() for t in a.get("tags", [])):
            score += 5
        if score > 0:
            results.append({**a, "_score": score})
    results.sort(key=lambda r: r["_score"], reverse=True)
    for r in results:
        del r["_score"]
    return {"results": results[:limit], "total": len(results), "query": query}
