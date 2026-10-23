"""Platform export manager — export platform data for compliance and migration."""
from __future__ import annotations
import json
import csv
import io


def export_platform_data(*, data_type: str, records: list[dict],
                           fmt: str = "json") -> dict:
    if not records:
        return {"status": "empty", "format": fmt, "size_bytes": 0}
    if fmt == "json":
        content = json.dumps({"data_type": data_type, "records": records,
                               "count": len(records)}, indent=2)
    elif fmt == "csv":
        buf = io.StringIO()
        if records:
            writer = csv.DictWriter(buf, fieldnames=sorted(records[0].keys()),
                                     extrasaction="ignore")
            writer.writeheader()
            for r in records:
                writer.writerow(r)
        content = buf.getvalue()
    elif fmt == "ndjson":
        content = "\n".join(json.dumps(r) for r in records)
    else:
        return {"status": "error", "message": f"Unsupported format: {fmt}"}
    size = len(content.encode())
    return {
        "status": "completed", "data_type": data_type,
        "format": fmt, "record_count": len(records),
        "size_bytes": size,
        "size_display": f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B",
        "content": content,
    }


def list_exportable_types() -> list[dict]:
    return [
        {"type": "users", "description": "All user profiles", "supports": ["json", "csv"]},
        {"type": "apps", "description": "Registered applications", "supports": ["json", "csv"]},
        {"type": "audit_logs", "description": "Audit trail events", "supports": ["json", "ndjson"]},
        {"type": "webhooks", "description": "Webhook configurations", "supports": ["json"]},
        {"type": "analytics", "description": "Usage analytics data", "supports": ["json", "csv", "ndjson"]},
    ]
