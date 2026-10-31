"""App analytics export — export analytics data in various formats."""

import json
import csv
import io
import html
from datetime import datetime, timezone


def export_analytics(*, data_points: list[dict], format: str = "json",
                       metrics: list[str] | None = None) -> dict:
    if not metrics:
        metrics = list(data_points[0].keys()) if data_points else []
    filtered = [{k: dp.get(k) for k in metrics} for dp in data_points]
    if format == "csv":
        buf = io.StringIO()
        if filtered:
            writer = csv.DictWriter(buf, fieldnames=metrics, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(filtered)
        content = buf.getvalue()
    else:
        content = json.dumps(filtered, indent=2, default=str)
    return {
        "format": format, "content": content,
        "row_count": len(filtered), "column_count": len(metrics),
        "size_bytes": len(content.encode()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
