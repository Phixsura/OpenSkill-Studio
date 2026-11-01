"""Analytics export — export app analytics data in multiple formats."""
from __future__ import annotations
import json
import csv
import io


def export_analytics(*, app_id: str, metrics: list[dict],
                        fmt: str = "json", period: str = "30d") -> dict:
    if fmt == "json":
        content = json.dumps({"app_id": app_id, "period": period,
                               "metrics": metrics}, indent=2)
    elif fmt == "csv":
        buf = io.StringIO()
        if metrics:
            writer = csv.DictWriter(buf, fieldnames=sorted(metrics[0].keys()), extrasaction="ignore")
            writer.writeheader()
            for m in metrics:
                writer.writerow(m)
        content = buf.getvalue()
    else:
        return {"error": f"Unsupported format: {fmt}"}
    size = len(content.encode())
    return {"app_id": app_id, "format": fmt, "period": period,
            "record_count": len(metrics), "size_bytes": size,
            "size_display": f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B",
            "content": content}
