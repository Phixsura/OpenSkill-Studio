"""Consumer API Pagination Helper — cursor/offset pagination with metadata."""
from __future__ import annotations

import base64
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class PaginationConfig:
    default_page_size: int = 20
    max_page_size: int = 100
    strategy: str = "offset"  # offset, cursor


@dataclass
class PaginationHelper:
    """Provide cursor and offset-based pagination for API responses."""

    _config: PaginationConfig = field(default_factory=PaginationConfig)

    def configure(self, default_page_size: int = 20, max_page_size: int = 100,
                  strategy: str = "offset") -> dict:
        if default_page_size < 1:
            raise ValueError("default_page_size must be positive")
        if max_page_size < default_page_size:
            raise ValueError("max_page_size must be >= default_page_size")
        if strategy not in ("offset", "cursor"):
            raise ValueError(f"Invalid strategy: {strategy}")
        self._config = PaginationConfig(default_page_size, max_page_size, strategy)
        return {"default_page_size": default_page_size, "max_page_size": max_page_size,
                "strategy": strategy}

    def paginate_offset(self, items: list, page: int = 1,
                        page_size: int | None = None) -> dict:
        size = min(page_size or self._config.default_page_size, self._config.max_page_size)
        if page < 1:
            raise ValueError("Page must be >= 1")
        total = len(items)
        total_pages = max(1, (total + size - 1) // size)
        start = (page - 1) * size
        end = start + size
        page_items = items[start:end]
        return {
            "data": page_items,
            "meta": {
                "page": page,
                "page_size": size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }

    def _encode_cursor(self, offset: int) -> str:
        return base64.urlsafe_b64encode(f"off:{offset}".encode()).decode()

    def _decode_cursor(self, cursor: str) -> int:
        try:
            decoded = base64.urlsafe_b64decode(cursor).decode()
            if decoded.startswith("off:"):
                return int(decoded[4:])
        except Exception:
            pass
        raise ValueError("Invalid cursor")

    def paginate_cursor(self, items: list, cursor: str | None = None,
                        page_size: int | None = None) -> dict:
        size = min(page_size or self._config.default_page_size, self._config.max_page_size)
        if cursor:
            offset = self._decode_cursor(cursor)
        else:
            offset = 0
        end = offset + size
        page_items = items[offset:end]
        has_more = end < len(items)
        next_cursor = self._encode_cursor(end) if has_more else None
        return {
            "data": page_items,
            "meta": {
                "cursor": cursor,
                "next_cursor": next_cursor,
                "has_more": has_more,
                "page_size": size,
                "returned": len(page_items),
            },
        }

    def paginate(self, items: list, **kwargs) -> dict:
        if self._config.strategy == "cursor":
            return self.paginate_cursor(items, cursor=kwargs.get("cursor"),
                                         page_size=kwargs.get("page_size"))
        return self.paginate_offset(items, page=kwargs.get("page", 1),
                                     page_size=kwargs.get("page_size"))

    def get_config(self) -> dict:
        return {
            "default_page_size": self._config.default_page_size,
            "max_page_size": self._config.max_page_size,
            "strategy": self._config.strategy,
        }
