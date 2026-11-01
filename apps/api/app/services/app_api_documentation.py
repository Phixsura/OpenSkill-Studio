"""App API Documentation — manage API documentation pages.

Manages API docs:
- Register documentation pages with content
- Organize by section/category
- Track page view counts
- Per-installation scoped docs
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DocPage:
    """An API documentation page."""

    page_id: str
    title: str
    content: str
    section: str = "general"
    sort_order: int = 0
    view_count: int = 0


class AppAPIDocumentation:
    """Manage API documentation pages."""

    def __init__(self) -> None:
        self._pages: dict[tuple[str, str], DocPage] = {}

    def create_page(
        self, installation_id: str, page_id: str, title: str,
        content: str, section: str = "general", sort_order: int = 0,
    ) -> DocPage:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not title:
            raise ValueError("title is required")

        page = DocPage(
            page_id=page_id, title=title, content=content,
            section=section, sort_order=sort_order,
        )
        self._pages[(installation_id, page_id)] = page
        return page

    def update_content(self, installation_id: str, page_id: str, content: str) -> DocPage:
        p = self._get(installation_id, page_id)
        p.content = content
        return p

    def record_view(self, installation_id: str, page_id: str) -> DocPage:
        p = self._get(installation_id, page_id)
        p.view_count += 1
        return p

    def list_pages(self, installation_id: str, section: str | None = None) -> list[DocPage]:
        pages = [p for (inst, _), p in self._pages.items() if inst == installation_id]
        if section:
            pages = [p for p in pages if p.section == section]
        return sorted(pages, key=lambda p: p.sort_order)

    def sections(self, installation_id: str) -> list[str]:
        s: set[str] = set()
        for (inst, _), p in self._pages.items():
            if inst == installation_id:
                s.add(p.section)
        return sorted(s)

    def search(self, installation_id: str, query: str) -> list[DocPage]:
        q = query.lower()
        return [
            p for (inst, _), p in self._pages.items()
            if inst == installation_id and (q in p.title.lower() or q in p.content.lower())
        ]

    def _get(self, installation_id: str, page_id: str) -> DocPage:
        key = (installation_id, page_id)
        p = self._pages.get(key)
        if p is None:
            raise KeyError(f"Page {page_id} not found")
        return p
