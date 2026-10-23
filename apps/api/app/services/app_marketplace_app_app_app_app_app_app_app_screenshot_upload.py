"""App screenshot uploader — validate and manage app listing screenshots."""
from __future__ import annotations
from urllib.parse import urlparse

MAX_SCREENSHOTS = 8
ALLOWED_FORMATS = [".png", ".jpg", ".jpeg", ".webp"]
MAX_SIZE_MB = 5


def validate_screenshot(*, filename: str, size_bytes: int, width: int, height: int) -> dict:
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    errors = []
    if ext not in ALLOWED_FORMATS:
        errors.append(f"Format {ext} not allowed")
    if size_bytes > MAX_SIZE_MB * 1024 * 1024:
        errors.append(f"Max {MAX_SIZE_MB}MB")
    if width < 640 or height < 400:
        errors.append("Minimum 640x400px")
    if width > 3840 or height > 2160:
        errors.append("Maximum 3840x2160px")
    return {"valid": len(errors) == 0, "errors": errors,
            "filename": filename, "dimensions": f"{width}x{height}"}


def reorder_screenshots(screenshots: list[str], *, from_idx: int, to_idx: int) -> list[str]:
    if from_idx < 0 or to_idx < 0 or from_idx >= len(screenshots) or to_idx >= len(screenshots):
        return screenshots
    item = screenshots.pop(from_idx)
    screenshots.insert(to_idx, item)
    return screenshots
