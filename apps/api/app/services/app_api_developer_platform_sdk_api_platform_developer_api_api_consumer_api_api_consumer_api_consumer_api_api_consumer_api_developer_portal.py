"""Consumer API Developer Portal — manage developer portal configuration."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PortalConfig:
    portal_id: str
    title: str
    logo_url: str = ""
    primary_color: str = "#3B82F6"
    custom_domain: str = ""
    show_changelog: bool = True
    show_status_page: bool = True
    show_playground: bool = True
    show_sdk_downloads: bool = True
    footer_text: str = ""

@dataclass
class PortalPage:
    page_id: str
    title: str
    slug: str
    content: str
    order: int = 0
    published: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiDeveloperPortal:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], PortalConfig] = {}
        self._pages: dict[tuple[str, str], PortalPage] = {}

    def set_config(self, installation_id: str, config: PortalConfig) -> PortalConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not config.title:
            raise ValueError("title is required")
        if config.primary_color and not config.primary_color.startswith("#"):
            raise ValueError("primary_color must be a hex color")
        self._configs[(installation_id, config.portal_id)] = config
        return config

    def get_config(self, installation_id: str, portal_id: str) -> PortalConfig | None:
        return self._configs.get((installation_id, portal_id))

    def add_page(self, installation_id: str, portal_id: str, page: PortalPage) -> PortalPage:
        if (installation_id, portal_id) not in self._configs:
            raise ValueError("Portal not configured")
        key = (installation_id, page.page_id)
        if key in self._pages:
            raise ValueError(f"Page {page.page_id} already exists")
        self._pages[key] = page
        return page

    def list_pages(self, installation_id: str, published_only: bool = False) -> list[PortalPage]:
        pages = [p for (inst, _), p in self._pages.items() if inst == installation_id]
        if published_only:
            pages = [p for p in pages if p.published]
        return sorted(pages, key=lambda p: p.order)

    def get_page_by_slug(self, installation_id: str, slug: str) -> PortalPage | None:
        for (inst, _), p in self._pages.items():
            if inst == installation_id and p.slug == slug:
                return p
        return None
