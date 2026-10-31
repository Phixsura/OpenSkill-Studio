"""Data table builder — sortable, filterable, paginated tables."""
from __future__ import annotations


def build_table(*, rows: list[dict], columns: list[str],
                 page: int = 1, page_size: int = 25,
                 sort_by: str | None = None, sort_dir: str = "asc",
                 filter_col: str | None = None, filter_val: str | None = None) -> dict:
    filtered = rows
    if filter_col and filter_val:
        filtered = [r for r in filtered if filter_val.lower() in str(r.get(filter_col, "")).lower()]
    if sort_by and sort_by in columns:
        reverse = sort_dir == "desc"
        filtered = sorted(filtered, key=lambda r: r.get(sort_by, ""), reverse=reverse)
    total = len(filtered)
    total_pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size
    page_rows = filtered[start:start + page_size]
    return {
        "rows": page_rows, "columns": columns,
        "total_rows": total, "page": page, "page_size": page_size,
        "total_pages": total_pages,
        "has_prev": page > 1, "has_next": page < total_pages,
        "showing": f"{start + 1}-{min(start + page_size, total)} of {total}",
    }
