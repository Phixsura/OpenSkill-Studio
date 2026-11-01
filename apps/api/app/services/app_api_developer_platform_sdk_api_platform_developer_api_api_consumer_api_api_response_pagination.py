"""API Consumer Response Pagination — standardize pagination across API responses."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PaginationConfig:
    consumer_id: str
    default_page_size: int = 20
    max_page_size: int = 100
    style: str = "offset"  # "offset", "cursor", "keyset"

@dataclass
class PaginatedResult:
    data: list
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

VALID_STYLES = {"offset", "cursor", "keyset"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponsePagination:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], PaginationConfig] = {}

    def configure(self, installation_id: str, config: PaginationConfig) -> PaginationConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.style not in VALID_STYLES: raise ValueError(f"Invalid style: {config.style}")
        if config.default_page_size < 1: raise ValueError("default_page_size must be >= 1")
        if config.max_page_size < config.default_page_size: raise ValueError("max must be >= default")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def paginate(self, installation_id: str, consumer_id: str, items: list, page: int = 1, page_size: int | None = None) -> PaginatedResult:
        config = self._configs.get((installation_id, consumer_id))
        ps = page_size or (config.default_page_size if config else 20)
        max_ps = config.max_page_size if config else 100
        ps = min(ps, max_ps)
        if page < 1: page = 1
        total = len(items)
        total_pages = max(1, (total + ps - 1) // ps)
        start = (page - 1) * ps
        end = start + ps
        return PaginatedResult(data=items[start:end], total=total, page=page, page_size=ps, total_pages=total_pages, has_next=page < total_pages, has_prev=page > 1)

    def get_config(self, installation_id: str, consumer_id: str) -> PaginationConfig | None:
        return self._configs.get((installation_id, consumer_id))

    def list_configs(self, installation_id: str) -> list[PaginationConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
