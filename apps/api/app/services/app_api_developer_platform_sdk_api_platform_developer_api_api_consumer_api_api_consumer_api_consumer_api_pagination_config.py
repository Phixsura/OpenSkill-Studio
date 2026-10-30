"""Consumer API Pagination Config — configure pagination behavior per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PaginationConfig:
    consumer_id: str
    default_page_size: int = 20
    max_page_size: int = 100
    strategy: str = "cursor"  # "cursor", "offset", "keyset"
    cursor_param: str = "cursor"
    page_param: str = "page"
    size_param: str = "page_size"

@dataclass
class PaginationParams:
    page_size: int
    cursor: str | None = None
    offset: int | None = None
    strategy: str = "cursor"

@dataclass
class PaginationMeta:
    page_size: int
    has_more: bool
    next_cursor: str | None = None
    total_count: int | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], PaginationConfig] = {}

    def set_config(self, installation_id: str, config: PaginationConfig) -> PaginationConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.default_page_size < 1:
            raise ValueError("default_page_size must be positive")
        if config.max_page_size < config.default_page_size:
            raise ValueError("max_page_size must be >= default_page_size")
        if config.strategy not in ("cursor", "offset", "keyset"):
            raise ValueError(f"Invalid strategy: {config.strategy}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def resolve(self, installation_id: str, consumer_id: str, requested_size: int | None = None) -> PaginationParams:
        config = self._configs.get((installation_id, consumer_id), PaginationConfig(consumer_id=consumer_id))
        size = requested_size if requested_size else config.default_page_size
        size = min(size, config.max_page_size)
        size = max(1, size)
        return PaginationParams(page_size=size, strategy=config.strategy)

    def build_meta(self, installation_id: str, consumer_id: str, returned_count: int, total: int | None = None, next_cursor: str | None = None) -> PaginationMeta:
        config = self._configs.get((installation_id, consumer_id), PaginationConfig(consumer_id=consumer_id))
        params = self.resolve(installation_id, consumer_id)
        has_more = returned_count >= params.page_size
        return PaginationMeta(page_size=params.page_size, has_more=has_more, next_cursor=next_cursor, total_count=total)

    def get_config(self, installation_id: str, consumer_id: str) -> PaginationConfig | None:
        return self._configs.get((installation_id, consumer_id))
