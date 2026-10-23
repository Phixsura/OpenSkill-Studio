"""Pagination — cursor and offset pagination helpers."""

import hashlib
import base64


def offset_paginate(*, total: int, page: int = 1, page_size: int = 20) -> dict:
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    total_pages = max(1, -(-total // page_size))  # ceil division
    offset = (page - 1) * page_size
    return {"page": page, "page_size": page_size, "total": total,
            "total_pages": total_pages, "offset": offset,
            "has_prev": page > 1, "has_next": page < total_pages,
            "prev_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None}


def cursor_paginate(*, items: list, page_size: int = 20, cursor: str | None = None) -> dict:
    start = 0
    if cursor:
        try:
            start = int(base64.urlsafe_b64decode(cursor).decode())
        except Exception:
            start = 0
    end = start + page_size
    page_items = items[start:end]
    next_cursor = base64.urlsafe_b64encode(str(end).encode()).decode() if end < len(items) else None
    return {"items": page_items, "count": len(page_items),
            "next_cursor": next_cursor, "has_more": end < len(items)}
