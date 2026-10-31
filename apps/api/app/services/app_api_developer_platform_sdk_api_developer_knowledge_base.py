"""App API Developer Knowledge Base — searchable developer knowledge base."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class KBArticle:
    article_id: str
    title: str
    content: str
    category: str  # "getting_started", "api_reference", "troubleshooting", "best_practices", "faq"
    tags: list[str] = field(default_factory=list)
    views: int = 0
    helpful_votes: int = 0

class AppAPIDeveloperPlatformSDKApiDeveloperKnowledgeBase:
    def __init__(self) -> None:
        self._articles: dict[tuple[str, str], KBArticle] = {}

    def add(self, installation_id: str, article_id: str, title: str, content: str, category: str, tags: list[str] | None = None) -> KBArticle:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"getting_started", "api_reference", "troubleshooting", "best_practices", "faq"}
        if category not in valid: raise ValueError("invalid category")
        key = (installation_id, article_id)
        if key in self._articles: raise ValueError(f"Article {article_id} exists")
        a = KBArticle(article_id=article_id, title=title, content=content, category=category, tags=tags or [])
        self._articles[key] = a
        return a

    def search(self, installation_id: str, query: str, category: str | None = None) -> list[KBArticle]:
        q = query.lower()
        articles = [a for (inst, _), a in self._articles.items() if inst == installation_id]
        if category: articles = [a for a in articles if a.category == category]
        scored = []
        for a in articles:
            score = 0
            if q in a.title.lower(): score += 10
            if q in a.content.lower(): score += 5
            if any(q in t.lower() for t in a.tags): score += 3
            if score > 0: scored.append((score, a))
        return [a for _, a in sorted(scored, key=lambda x: x[0], reverse=True)]

    def view(self, installation_id: str, article_id: str) -> KBArticle:
        key = (installation_id, article_id)
        a = self._articles.get(key)
        if a is None: raise KeyError(f"Article {article_id} not found")
        a.views += 1
        return a

    def popular(self, installation_id: str, limit: int = 10) -> list[KBArticle]:
        articles = [a for (inst, _), a in self._articles.items() if inst == installation_id]
        return sorted(articles, key=lambda a: a.views, reverse=True)[:limit]

    def category_counts(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), a in self._articles.items():
            if inst == installation_id: counts[a.category] = counts.get(a.category, 0) + 1
        return counts
