"""Screenshot manager — validate and organize app listing screenshots."""

ALLOWED_FORMATS = {"png", "jpg", "jpeg", "webp"}
MAX_SCREENSHOTS = 10
MAX_SIZE_MB = 5


def validate_screenshot(*, filename: str, size_bytes: int) -> dict:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    errors = []
    if ext not in ALLOWED_FORMATS:
        errors.append(f"Invalid format '{ext}'. Use: {', '.join(sorted(ALLOWED_FORMATS))}")
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        errors.append(f"File too large ({size_mb:.1f}MB). Max: {MAX_SIZE_MB}MB")
    return {"valid": len(errors) == 0, "errors": errors, "format": ext, "size_mb": round(size_mb, 2)}


def reorder_screenshots(*, screenshots: list[dict], new_order: list[str]) -> list[dict]:
    by_id = {s["id"]: s for s in screenshots}
    ordered = []
    for sid in new_order:
        if sid in by_id:
            ordered.append({**by_id[sid], "position": len(ordered)})
    return ordered


def get_screenshot_requirements() -> dict:
    return {"max_count": MAX_SCREENSHOTS, "max_size_mb": MAX_SIZE_MB,
            "allowed_formats": sorted(ALLOWED_FORMATS),
            "recommended_size": "1280x720", "min_screenshots": 1}
