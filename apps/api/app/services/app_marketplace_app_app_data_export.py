"""Data export — serialize data to CSV/JSON with streaming support."""

import csv
import io
import json
import html
from datetime import datetime, timezone


def export_to_csv(*, columns: list[str], rows: list[dict]) -> dict:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        safe = {k: str(v) for k, v in row.items() if k in set(columns)}
        writer.writerow(safe)
    content = buf.getvalue()
    return {"format": "csv", "content": content, "row_count": len(rows),
            "size_bytes": len(content.encode()), "columns": columns}


def export_to_json(*, rows: list[dict], pretty: bool = False) -> dict:
    content = json.dumps(rows, indent=2 if pretty else None, default=str)
    return {"format": "json", "content": content, "row_count": len(rows),
            "size_bytes": len(content.encode())}


def build_export_options(*, row_count: int, columns: list[str]) -> dict:
    return {"formats": [
        {"id": "csv", "label": "CSV", "icon": "📊", "description": "Spreadsheet compatible"},
        {"id": "json", "label": "JSON", "icon": "📋", "description": "Developer friendly"},
    ], "row_count": row_count, "column_count": len(columns)}
