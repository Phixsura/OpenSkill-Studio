"""Pagination helper — cursor and offset pagination utilities."""
from __future__ import annotations
import math


def paginate_offset(*, total: int, page: int = 1, page_size: int = 25) -> dict:
    total_pages = max(1, math.ceil(total / page_size))
    page = max(1, min(page, total_pages))
    offset = (page - 1) * page_size
    return {
        "page": page, "page_size": page_size, "total": total,
        "total_pages": total_pages, "offset": offset,
        "has_prev": page > 1, "has_next": page < total_pages,
        "showing": f"{offset + 1}-{min(offset + page_size, total)} of {total}",
        "pages": _page_numbers(page, total_pages),
    }


def paginate_cursor(*, items: list, cursor: str | None = None,
                      limit: int = 25, id_field: str = "id") -> dict:
    if cursor:
        start_idx = next((i for i, item in enumerate(items) if str(item.get(id_field)) == cursor), 0) + 1
    else:
        start_idx = 0
    page_items = items[start_idx:start_idx + limit]
    next_cursor = str(page_items[-1][id_field]) if start_idx + limit < len(items) else None
    return {"items": page_items, "next_cursor": next_cursor,
            "has_more": next_cursor is not None, "count": len(page_items)}


def _page_numbers(current: int, total: int, window: int = 2) -> list[int]:
    start = max(1, current - window)
    end = min(total, current + window)
    return list(range(start, end + 1))
