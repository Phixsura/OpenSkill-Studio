"""App screenshot gallery — manage and display app screenshots."""
from __future__ import annotations
import html
from urllib.parse import urlparse


def build_screenshot_gallery(screenshots: list[dict], *, app_name: str = "") -> dict:
    items = []
    for s in screenshots:
        url = s.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme not in ("https",):
            continue  # skip non-HTTPS
        items.append({
            "url": url, "alt": html.escape(s.get("alt", f"{app_name} screenshot")),
            "caption": html.escape(s.get("caption", "")[:200]),
            "width": s.get("width", 0), "height": s.get("height", 0),
        })
    return {"screenshots": items, "count": len(items), "app_name": html.escape(app_name)}


def validate_screenshots(screenshots: list[dict]) -> dict:
    errors = []
    for i, s in enumerate(screenshots):
        url = s.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https":
            errors.append({"index": i, "error": "Must use HTTPS"})
        if not s.get("alt"):
            errors.append({"index": i, "error": "Missing alt text"})
    return {"valid": len(errors) == 0, "errors": errors, "total": len(screenshots)}
