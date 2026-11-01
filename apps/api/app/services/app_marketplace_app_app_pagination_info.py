"""Pagination info — descriptive pagination text and controls."""


def build_pagination_info(*, page: int, per_page: int, total: int) -> dict:
    total_pages = max((total + per_page - 1) // per_page, 1)
    start = (page - 1) * per_page + 1
    end = min(page * per_page, total)
    return {
        "page": page, "per_page": per_page, "total": total,
        "total_pages": total_pages,
        "start_item": start if total > 0 else 0,
        "end_item": end,
        "display": f"{start}-{end} of {total}" if total > 0 else "No results",
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "pages": list(range(max(1, page - 2), min(total_pages + 1, page + 3))),
    }
