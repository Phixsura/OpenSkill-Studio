"""URL shortener — generate short links with analytics tracking."""

import hashlib
import html
from urllib.parse import urlparse


def _safe_url(url: str) -> str | None:
    parsed = urlparse(url)
    return url if parsed.scheme in ("https", "http") else None


def shorten_url(*, url: str, custom_slug: str | None = None) -> dict:
    safe = _safe_url(url)
    if not safe:
        return {"error": "Invalid URL scheme"}
    slug = custom_slug or hashlib.sha256(url.encode()).hexdigest()[:8]
    short = f"https://osk.li/{slug}"
    return {"original": safe, "short": short, "slug": slug}


def build_link_analytics(*, links: list[dict]) -> dict:
    items = []
    total_clicks = 0
    for l in links:
        clicks = l.get("clicks", 0)
        total_clicks += clicks
        items.append({
            "slug": l["slug"],
            "original": html.escape(l.get("original", "")),
            "clicks": clicks,
            "created_at": l.get("created_at", ""),
        })
    items.sort(key=lambda x: x["clicks"], reverse=True)
    return {"links": items, "total_links": len(items), "total_clicks": total_clicks}
