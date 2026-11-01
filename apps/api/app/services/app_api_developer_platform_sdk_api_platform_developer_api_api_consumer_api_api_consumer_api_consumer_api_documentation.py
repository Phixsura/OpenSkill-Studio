"""Consumer API Documentation — manage per-consumer API docs and guides."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class DocPage:
    page_id: str
    title: str
    content: str
    category: str = "guide"  # "guide", "reference", "tutorial", "faq"
    version: str = "latest"
    published: bool = False
    updated_at: datetime | None = None
    order: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentation:
    def __init__(self) -> None:
        self._pages: dict[tuple[str, str], DocPage] = {}

    def create_page(self, installation_id: str, page: DocPage) -> DocPage:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not page.title:
            raise ValueError("title is required")
        if len(page.content) > 100000:
            raise ValueError("Content too long (max 100KB)")
        key = (installation_id, page.page_id)
        if key in self._pages:
            raise ValueError(f"Page {page.page_id} already exists")
        page.updated_at = page.updated_at or datetime.utcnow()
        self._pages[key] = page
        return page

    def update_page(self, installation_id: str, page_id: str, title: str | None = None, content: str | None = None, published: bool | None = None) -> DocPage:
        key = (installation_id, page_id)
        page = self._pages.get(key)
        if not page:
            raise ValueError("Page not found")
        if title is not None:
            page.title = title
        if content is not None:
            if len(content) > 100000:
                raise ValueError("Content too long")
            page.content = content
        if published is not None:
            page.published = published
        page.updated_at = datetime.utcnow()
        return page

    def get_page(self, installation_id: str, page_id: str) -> DocPage | None:
        return self._pages.get((installation_id, page_id))

    def list_pages(self, installation_id: str, category: str | None = None, published_only: bool = False) -> list[DocPage]:
        pages = [p for (inst, _), p in self._pages.items() if inst == installation_id]
        if category:
            pages = [p for p in pages if p.category == category]
        if published_only:
            pages = [p for p in pages if p.published]
        return sorted(pages, key=lambda p: (p.category, p.order))

    def search(self, installation_id: str, query: str) -> list[DocPage]:
        q = query.lower()
        return [p for (inst, _), p in self._pages.items() if inst == installation_id and (q in p.title.lower() or q in p.content.lower())]
