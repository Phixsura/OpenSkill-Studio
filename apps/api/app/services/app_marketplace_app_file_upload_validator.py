"""File upload validator — validate file uploads for size, type, and safety."""

import re

ALLOWED_TYPES = {
    "image": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"},
    "document": {".pdf", ".md", ".txt", ".json", ".yaml", ".yml"},
    "archive": {".zip", ".tar.gz", ".tgz"},
}
MAX_SIZES_MB = {"image": 5, "document": 10, "archive": 50}


def validate_upload(*, filename: str, size_bytes: int, category: str) -> dict:
    if category not in ALLOWED_TYPES:
        return {"valid": False, "error": f"Invalid category. Valid: {', '.join(sorted(ALLOWED_TYPES))}"}
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    errors = []
    if ext not in ALLOWED_TYPES[category]:
        errors.append(f"File type {ext} not allowed. Allowed: {', '.join(sorted(ALLOWED_TYPES[category]))}")
    max_mb = MAX_SIZES_MB.get(category, 10)
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > max_mb:
        errors.append(f"File too large: {size_mb:.1f}MB (max {max_mb}MB)")
    # Block dangerous filenames
    if re.search(r"[<>:\"/\\|?*\x00-\x1f]", filename):
        errors.append("Filename contains invalid characters")
    return {"valid": len(errors) == 0, "errors": errors, "filename": filename,
            "size_mb": round(size_mb, 2), "category": category}
