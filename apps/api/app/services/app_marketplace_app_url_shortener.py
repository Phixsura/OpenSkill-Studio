"""URL shortener — create and resolve short links for apps."""

import secrets
import re

URL_RE = re.compile(r"^https?://[^\s]+$")


def create_short_link(*, url: str, custom_slug: str | None = None) -> dict:
    if not URL_RE.match(url):
        return {"error": "Invalid URL"}
    slug = custom_slug or secrets.token_urlsafe(6)
    if custom_slug and not re.match(r"^[a-zA-Z0-9_-]{3,30}$", custom_slug):
        return {"error": "Custom slug must be 3-30 alphanumeric characters"}
    return {
        "short_url": f"https://osk.link/{slug}",
        "original_url": url,
        "slug": slug,
        "clicks": 0,
    }


def get_link_analytics(*, links: list[dict]) -> dict:
    total_clicks = sum(l.get("clicks", 0) for l in links)
    top = sorted(links, key=lambda l: l.get("clicks", 0), reverse=True)[:5]
    return {
        "total_links": len(links),
        "total_clicks": total_clicks,
        "avg_clicks": round(total_clicks / max(len(links), 1), 1),
        "top_links": [{"slug": l.get("slug"), "clicks": l.get("clicks", 0)} for l in top],
    }
