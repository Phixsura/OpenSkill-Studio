"""Analytics export — export analytics data in various formats."""

import csv
import io
import json
from datetime import datetime


def export_analytics(*, app_id: str, data: list[dict], fmt: str = "json") -> dict:
    valid_formats = {"json", "csv", "markdown"}
    if fmt not in valid_formats:
        return {"error": f"Invalid format. Valid: {', '.join(sorted(valid_formats))}"}
    if not data:
        return {"error": "No data to export"}

    if fmt == "json":
        content = json.dumps(data, indent=2)
        mime = "application/json"
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        content = buf.getvalue()
        mime = "text/csv"
    else:  # markdown
        headers = list(data[0].keys())
        lines = ["| " + " | ".join(headers) + " |",
                 "| " + " | ".join("---" for _ in headers) + " |"]
        for row in data:
            lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
        content = "\n".join(lines)
        mime = "text/markdown"

    return {
        "app_id": app_id,
        "format": fmt,
        "mime_type": mime,
        "content": content,
        "row_count": len(data),
        "exported_at": datetime.utcnow().isoformat(),
    }
