"""Knowledge base — searchable documentation articles."""
from __future__ import annotations
import html


_articles: dict[str, dict] = {}


def create_article(slug: str, title: str, content: str, category: str, tags: list[str] | None = None) -> dict:
    _articles[slug] = {"slug": slug, "title": html.escape(title),
                        "content": html.escape(content), "category": category,
                        "tags": tags or [], "views": 0, "helpful": 0, "not_helpful": 0}
    return _articles[slug]


def search_articles(query: str, category: str | None = None) -> list[dict]:
    q = query.lower()
    results = []
    for a in _articles.values():
        if category and a["category"] != category:
            continue
        if q in a["title"].lower() or q in a["content"].lower() or any(q in t.lower() for t in a["tags"]):
            results.append(a)
    return results


def rate_article(slug: str, helpful: bool) -> dict:
    a = _articles.get(slug)
    if not a:
        return {"rated": False, "error": "not_found"}
    if helpful:
        a["helpful"] += 1
    else:
        a["not_helpful"] += 1
    total = a["helpful"] + a["not_helpful"]
    return {"rated": True, "helpful_pct": round(a["helpful"] / max(total, 1) * 100)}


def kb_stats() -> dict:
    by_cat: dict[str, int] = {}
    for a in _articles.values():
        by_cat[a["category"]] = by_cat.get(a["category"], 0) + 1
    return {"total": len(_articles), "by_category": by_cat,
            "categories": sorted(by_cat.keys())}


def clear_kb() -> None:
    _articles.clear()
