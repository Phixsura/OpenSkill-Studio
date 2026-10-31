"""Data export request — GDPR-style data portability for app data."""

from datetime import datetime, timezone


def create_export_request(*, developer_id: str, export_type: str, format: str = "json") -> dict:
    valid_types = {"full", "apps", "analytics", "reviews", "installations"}
    valid_formats = {"json", "csv"}
    if export_type not in valid_types:
        return {"error": f"Invalid type. Use: {', '.join(sorted(valid_types))}"}
    if format not in valid_formats:
        return {"error": f"Invalid format. Use: {', '.join(sorted(valid_formats))}"}
    return {
        "developer_id": developer_id, "export_type": export_type, "format": format,
        "status": "queued", "created_at": datetime.now(timezone.utc).isoformat(),
        "estimated_size_mb": None, "download_url": None, "error": None,
    }


def estimate_export_size(*, app_count: int, install_count: int, review_count: int) -> dict:
    base_kb = 50
    per_app_kb = 10
    per_install_kb = 2
    per_review_kb = 1
    total_kb = base_kb + app_count * per_app_kb + install_count * per_install_kb + review_count * per_review_kb
    return {"estimated_kb": total_kb, "estimated_mb": round(total_kb / 1024, 2)}


def complete_export(*, request: dict, download_url: str, size_bytes: int) -> dict:
    return {**request, "status": "completed", "download_url": download_url,
            "size_bytes": size_bytes, "completed_at": datetime.now(timezone.utc).isoformat()}
