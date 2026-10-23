"""Screenshot gallery — manage and display app screenshots with metadata."""


def build_screenshot_gallery(*, screenshots: list[dict], max_display: int = 10) -> dict:
    items = []
    for i, s in enumerate(screenshots[:max_display]):
        items.append({"index": i, "url": s.get("url", ""), "alt": s.get("alt", f"Screenshot {i+1}"),
                       "width": s.get("width", 1280), "height": s.get("height", 720),
                       "thumbnail_url": s.get("thumbnail_url", s.get("url", ""))})
    return {"items": items, "count": len(items), "total": len(screenshots),
            "has_more": len(screenshots) > max_display,
            "aspect_ratio": "16:9"}


def validate_screenshot(*, width: int, height: int, size_bytes: int, format: str) -> dict:
    errors = []
    if width < 640:
        errors.append("Minimum width is 640px")
    if width > 3840:
        errors.append("Maximum width is 3840px")
    aspect = round(width / max(height, 1), 2)
    if aspect < 1.2 or aspect > 2.5:
        errors.append("Aspect ratio should be between 4:3 and 21:9")
    if size_bytes > 5 * 1024 * 1024:
        errors.append("Maximum file size is 5MB")
    if format not in ("png", "jpg", "jpeg", "webp"):
        errors.append(f"Unsupported format: {format}")
    return {"valid": len(errors) == 0, "errors": errors, "aspect_ratio": aspect}
