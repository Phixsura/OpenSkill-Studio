"""Documentation Hub — centralized docs for the developer platform.

Manages documentation pages with categories, search, versioning,
and reading progress tracking.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class DocPage:
    slug: str
    title: str
    category: str
    content: str
    order: int = 0


class ExtensionDocsHubService:
    """Manages platform documentation with search."""

    def __init__(self):
        self._pages: dict[str, DocPage] = {}
        self._read: dict[str, set[str]] = defaultdict(set)

    def add_page(self, slug: str, title: str, category: str,
                 content: str, order: int = 0) -> DocPage:
        page = DocPage(slug=slug, title=title, category=category,
                       content=content, order=order)
        self._pages[slug] = page
        return page

    def get_page(self, slug: str) -> DocPage | None:
        return self._pages.get(slug)

    def search(self, query: str) -> list[DocPage]:
        q = query.lower()
        return [p for p in self._pages.values()
                if q in p.title.lower() or q in p.content.lower()]

    def get_categories(self) -> dict[str, list[DocPage]]:
        cats: dict[str, list[DocPage]] = defaultdict(list)
        for p in self._pages.values():
            cats[p.category].append(p)
        for cat in cats:
            cats[cat].sort(key=lambda p: p.order)
        return dict(cats)

    def mark_read(self, user_id: str, slug: str) -> None:
        self._read[user_id].add(slug)

    def get_reading_progress(self, user_id: str) -> dict:
        total = len(self._pages)
        read = len(self._read.get(user_id, set()) & set(self._pages.keys()))
        return {"read": read, "total": total,
                "percent": round(read / max(total, 1) * 100)}
