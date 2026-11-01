"""App screenshot — screenshot management for app listings."""

import html
from urllib.parse import urlparse


def validate_screenshot(*, url: str, alt_text: str = "", order: int = 0) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return {"valid": False, "error": "Invalid URL scheme"}
    ext = parsed.path.rsplit(".", 1)[-1].lower() if "." in parsed.path else ""
    if ext not in ("png", "jpg", "jpeg", "webp", "gif"):
        return {"valid": False, "error": f"Unsupported format: {ext}"}
    return {"valid": True, "url": url, "alt_text": html.escape(alt_text),
            "order": order, "format": ext}


def build_screenshot_gallery(*, screenshots: list[dict]) -> dict:
    items = sorted(screenshots, key=lambda s: s.get("order", 0))
    valid = [s for s in items if s.get("valid", True)]
    return {"screenshots": valid, "total": len(valid),
            "meets_minimum": len(valid) >= 2,
            "formats": list(set(s.get("format", "") for s in valid if s.get("format")))}
