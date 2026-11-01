"""Pagination helper — compute pagination metadata."""


def paginate(*, total: int, page: int = 1, per_page: int = 20) -> dict:
    """Compute pagination metadata."""
    page = max(1, page)
    per_page = max(1, min(per_page, 100))
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    return {
        "page": page, "per_page": per_page, "total": total,
        "total_pages": total_pages, "offset": offset,
        "has_next": page < total_pages, "has_prev": page > 1,
    }
