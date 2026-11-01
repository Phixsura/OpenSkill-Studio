"""Extension Docs Engine — documentation generation and serving."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DocPage:
    slug: str
    title: str
    content: str
    category: str = "guide"  # guide, api, tutorial, reference
    order: int = 0


class ExtDocsEngineService:
    def __init__(self):
        self._pages: dict[str, dict[str, DocPage]] = {}  # ext_id -> {slug -> page}

    def add_page(self, extension_id: str, slug: str, title: str,
                 content: str, category: str = "guide", order: int = 0) -> DocPage:
        page = DocPage(slug=slug, title=title, content=content,
                       category=category, order=order)
        if extension_id not in self._pages:
            self._pages[extension_id] = {}
        self._pages[extension_id][slug] = page
        return page

    def get_page(self, extension_id: str, slug: str) -> DocPage | None:
        return self._pages.get(extension_id, {}).get(slug)

    def get_toc(self, extension_id: str) -> list[dict]:
        pages = self._pages.get(extension_id, {}).values()
        by_cat: dict[str, list[DocPage]] = {}
        for p in sorted(pages, key=lambda p: p.order):
            by_cat.setdefault(p.category, []).append(p)
        return [{"category": cat, "pages": [{"slug": p.slug, "title": p.title} for p in ps]}
                for cat, ps in by_cat.items()]

    def search(self, extension_id: str, query: str) -> list[DocPage]:
        q = query.lower()
        return [p for p in self._pages.get(extension_id, {}).values()
                if q in p.title.lower() or q in p.content.lower()]
