"""Pagination helper — cursor and offset pagination utilities."""

import base64
import hashlib


def paginate_offset(*, items: list, page: int = 1, per_page: int = 20) -> dict:
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20
    total = len(items)
    total_pages = max((total + per_page - 1) // per_page, 1)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "data": items[start:end],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


def paginate_cursor(*, items: list, cursor: str | None = None, limit: int = 20) -> dict:
    start = 0
    if cursor:
        try:
            start = int(base64.b64decode(cursor).decode())
        except Exception:
            start = 0
    end = start + limit
    page_items = items[start:end]
    next_cursor = base64.b64encode(str(end).encode()).decode() if end < len(items) else None
    return {
        "data": page_items,
        "meta": {
            "next_cursor": next_cursor,
            "has_more": next_cursor is not None,
            "count": len(page_items),
        },
    }
