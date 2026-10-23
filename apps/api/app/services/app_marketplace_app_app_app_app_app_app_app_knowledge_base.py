"""Platform knowledge base — searchable articles with categories and ratings."""
from __future__ import annotations
import html


class KnowledgeBase:
    def __init__(self):
        self._articles: dict[str, dict] = {}

    def add_article(self, *, slug: str, title: str, body: str,
                     category: str, tags: list[str] | None = None) -> dict:
        self._articles[slug] = {
            "slug": slug, "title": html.escape(title),
            "body": body, "category": category,
            "tags": tags or [], "views": 0, "helpful": 0, "not_helpful": 0,
        }
        return {"slug": slug, "title": html.escape(title)}

    def search(self, query: str, *, category: str | None = None, limit: int = 10) -> list[dict]:
        q = query.lower()
        results = []
        for a in self._articles.values():
            if category and a["category"] != category:
                continue
            if q in a["title"].lower() or q in a["body"].lower() or q in " ".join(a["tags"]).lower():
                results.append({"slug": a["slug"], "title": a["title"],
                                 "category": a["category"], "views": a["views"]})
        return results[:limit]

    def view(self, slug: str) -> dict:
        a = self._articles.get(slug)
        if not a:
            return {"error": "Article not found"}
        a["views"] += 1
        return {"slug": slug, "title": a["title"], "body": a["body"],
                "category": a["category"], "views": a["views"]}

    def rate(self, slug: str, *, helpful: bool) -> dict:
        a = self._articles.get(slug)
        if not a:
            return {"error": "Article not found"}
        if helpful:
            a["helpful"] += 1
        else:
            a["not_helpful"] += 1
        total = a["helpful"] + a["not_helpful"]
        return {"slug": slug, "helpful_pct": round(a["helpful"] / max(total, 1) * 100)}

    def stats(self) -> dict:
        return {"total_articles": len(self._articles),
                "total_views": sum(a["views"] for a in self._articles.values()),
                "categories": list({a["category"] for a in self._articles.values()})}
