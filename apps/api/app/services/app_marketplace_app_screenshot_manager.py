"""Screenshot manager — validate, order, and serve app screenshots."""

import re

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE_MB = 5
MAX_SCREENSHOTS = 10
MIN_SCREENSHOTS = 1
MIN_DIMENSIONS = (640, 360)


def validate_screenshot(*, filename: str, file_size_bytes: int,
                          width: int, height: int) -> dict:
    errors = []
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        errors.append(f"Invalid format: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    if file_size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
        errors.append(f"File too large: {file_size_bytes / 1024 / 1024:.1f}MB (max {MAX_FILE_SIZE_MB}MB)")
    if width < MIN_DIMENSIONS[0] or height < MIN_DIMENSIONS[1]:
        errors.append(f"Too small: {width}x{height} (min {MIN_DIMENSIONS[0]}x{MIN_DIMENSIONS[1]})")
    return {"valid": len(errors) == 0, "errors": errors, "filename": filename}


def reorder_screenshots(*, screenshots: list[dict], new_order: list[str]) -> dict:
    by_id = {s["id"]: s for s in screenshots}
    missing = [sid for sid in new_order if sid not in by_id]
    if missing:
        return {"success": False, "error": f"Unknown IDs: {', '.join(missing)}"}
    ordered = [by_id[sid] for sid in new_order]
    for i, s in enumerate(ordered):
        s["position"] = i
    return {"success": True, "screenshots": ordered}
