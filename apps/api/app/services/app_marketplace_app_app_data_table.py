"""Data table — sortable, filterable table configuration."""


def build_table_config(*, columns: list[dict], rows: list[dict],
                         sort_by: str | None = None, sort_dir: str = "asc",
                         page: int = 1, per_page: int = 10) -> dict:
    # Sort
    if sort_by:
        reverse = sort_dir == "desc"
        rows = sorted(rows, key=lambda r: r.get(sort_by, ""), reverse=reverse)
    # Paginate
    total = len(rows)
    start = (page - 1) * per_page
    page_rows = rows[start:start + per_page]
    return {
        "columns": columns,
        "rows": page_rows,
        "total_rows": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max((total + per_page - 1) // per_page, 1),
        "sort_by": sort_by,
        "sort_dir": sort_dir,
    }
