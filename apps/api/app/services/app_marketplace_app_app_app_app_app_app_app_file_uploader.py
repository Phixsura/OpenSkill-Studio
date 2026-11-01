"""File uploader — validate and process file uploads with size/type checks."""
from __future__ import annotations

ALLOWED_TYPES = {
    "image": {"extensions": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"], "max_mb": 10},
    "document": {"extensions": [".pdf", ".doc", ".docx", ".txt", ".md"], "max_mb": 25},
    "archive": {"extensions": [".zip", ".tar.gz", ".tgz"], "max_mb": 100},
    "code": {"extensions": [".js", ".ts", ".py", ".go", ".rs"], "max_mb": 5},
}


def validate_upload(*, filename: str, size_bytes: int, category: str = "image") -> dict:
    config = ALLOWED_TYPES.get(category)
    if not config:
        return {"valid": False, "error": f"Unknown category: {category}"}
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in config["extensions"]:
        return {"valid": False, "error": f"File type {ext} not allowed for {category}",
                "allowed": config["extensions"]}
    max_bytes = config["max_mb"] * 1024 * 1024
    if size_bytes > max_bytes:
        return {"valid": False, "error": f"File too large. Max: {config['max_mb']}MB",
                "max_bytes": max_bytes, "actual_bytes": size_bytes}
    size_display = f"{size_bytes / 1024:.1f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / 1024 / 1024:.1f} MB"
    return {"valid": True, "filename": filename, "extension": ext,
            "size_bytes": size_bytes, "size_display": size_display, "category": category}
