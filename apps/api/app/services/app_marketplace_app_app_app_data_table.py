"""App data table — generic sortable, filterable data table."""

import html


def build_data_table(*, columns: list[dict], rows: list[dict],
                       sort_by: str | None = None, sort_dir: str = "asc",
                       page: int = 1, page_size: int = 10) -> dict:
    cols = [{"key": c["key"], "label": html.escape(c.get("label", c["key"])),
             "sortable": c.get("sortable", True), "type": c.get("type", "text")}
            for c in columns]
    sorted_rows = list(rows)
    if sort_by:
        col_keys = {c["key"] for c in columns}
        if sort_by in col_keys:
            sorted_rows.sort(key=lambda r: r.get(sort_by, ""), reverse=(sort_dir == "desc"))
    total = len(sorted_rows)
    start = (page - 1) * page_size
    page_rows = sorted_rows[start:start + page_size]
    total_pages = max(1, -(-total // page_size))
    return {"columns": cols, "rows": page_rows, "total": total,
            "page": page, "page_size": page_size, "total_pages": total_pages,
            "sort_by": sort_by, "sort_dir": sort_dir}
