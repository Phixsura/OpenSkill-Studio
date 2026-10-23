"""Data export manager — generate CSV/JSON exports with progress tracking."""
from __future__ import annotations
import csv
import io
import json


def export_data(records: list[dict], *, fmt: str = "csv",
                columns: list[str] | None = None) -> dict:
    if not records:
        return {"status": "empty", "format": fmt, "rows": 0, "size_bytes": 0, "content": ""}
    cols = columns or sorted(records[0].keys())
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)
        content = buf.getvalue()
    elif fmt == "json":
        filtered = [{k: r.get(k) for k in cols} for r in records]
        content = json.dumps(filtered, indent=2)
    else:
        return {"status": "error", "message": f"Unsupported format: {fmt}"}
    return {"status": "complete", "format": fmt, "rows": len(records),
            "columns": cols, "size_bytes": len(content.encode()),
            "size_display": _human_size(len(content.encode())), "content": content}


def _human_size(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}" if b != int(b) else f"{b} {unit}"
        b /= 1024
    return f"{b:.1f} TB"
