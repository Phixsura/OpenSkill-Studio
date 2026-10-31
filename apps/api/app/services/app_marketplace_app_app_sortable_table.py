"""Sortable table — column-sortable data table builder."""

import html


def build_sortable_table(*, columns: list[dict], rows: list[dict],
                          sort_by: str | None = None, sort_dir: str = "asc") -> dict:
    cols = [{"key": c["key"], "label": html.escape(c.get("label", c["key"])),
             "sortable": c.get("sortable", True)} for c in columns]
    sorted_rows = list(rows)
    if sort_by:
        col_keys = {c["key"] for c in columns}
        if sort_by in col_keys:
            sorted_rows.sort(key=lambda r: r.get(sort_by, ""), reverse=(sort_dir == "desc"))
    safe_rows = [{k: html.escape(str(v)) if isinstance(v, str) else v for k, v in r.items()} for r in sorted_rows]
    return {"columns": cols, "rows": safe_rows, "sort_by": sort_by,
            "sort_dir": sort_dir, "total_rows": len(safe_rows)}
