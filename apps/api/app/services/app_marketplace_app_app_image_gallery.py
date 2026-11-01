"""Image gallery — screenshot/media gallery with lightbox support."""

import html
from urllib.parse import urlparse


def _safe_image_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http", "data"):
        return ""
    return url


def build_image_gallery(*, images: list[dict]) -> dict:
    items = []
    for img in images:
        src = _safe_image_url(img.get("src", ""))
        if not src:
            continue
        items.append({
            "src": src,
            "alt": html.escape(img.get("alt", "")),
            "caption": html.escape(img.get("caption", "")),
            "width": img.get("width"),
            "height": img.get("height"),
        })
    return {"images": items, "count": len(items)}
