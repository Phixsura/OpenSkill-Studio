"""Drag-drop uploader — file upload validation and processing."""

import html
import hashlib
import os

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".zip", ".tar.gz"}
MAX_FILE_SIZE_MB = 50


def validate_upload(*, filename: str, size_bytes: int, mime_type: str = "") -> dict:
    ext = os.path.splitext(filename)[1].lower()
    errors = []
    if ext not in ALLOWED_EXTENSIONS:
        errors.append(f"File type {ext} not allowed")
    size_mb = round(size_bytes / (1024 * 1024), 2)
    if size_mb > MAX_FILE_SIZE_MB:
        errors.append(f"File too large ({size_mb}MB, max {MAX_FILE_SIZE_MB}MB)")
    return {"filename": html.escape(filename), "extension": ext, "size_mb": size_mb,
            "valid": len(errors) == 0, "errors": errors}


def build_upload_summary(*, files: list[dict]) -> dict:
    total_size = sum(f.get("size_bytes", 0) for f in files)
    valid = [f for f in files if validate_upload(filename=f["name"], size_bytes=f.get("size_bytes", 0))["valid"]]
    return {"total_files": len(files), "valid_files": len(valid),
            "rejected_files": len(files) - len(valid),
            "total_size_mb": round(total_size / (1024 * 1024), 2)}
