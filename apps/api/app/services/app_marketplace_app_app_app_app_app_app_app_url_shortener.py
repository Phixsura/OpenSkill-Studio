"""URL shortener — create short links for sharing platform resources."""
from __future__ import annotations
import hashlib
from urllib.parse import urlparse


class UrlShortener:
    def __init__(self, *, base_url: str = "https://osk.io"):
        self._base = base_url
        self._links: dict[str, dict] = {}

    def shorten(self, url: str, *, custom_slug: str = "") -> dict:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {"error": "Invalid URL"}
        slug = custom_slug or hashlib.sha256(url.encode()).hexdigest()[:8]
        if slug in self._links:
            return {"error": "Slug already in use"}
        self._links[slug] = {"url": url, "slug": slug, "clicks": 0}
        return {"short_url": f"{self._base}/{slug}", "slug": slug, "original": url}

    def resolve(self, slug: str) -> dict:
        link = self._links.get(slug)
        if not link:
            return {"error": "Link not found"}
        link["clicks"] += 1
        return {"url": link["url"], "clicks": link["clicks"]}

    def stats(self, slug: str) -> dict:
        link = self._links.get(slug)
        if not link:
            return {"error": "Not found"}
        return {"slug": slug, "url": link["url"], "clicks": link["clicks"],
                "short_url": f"{self._base}/{slug}"}

    def list_links(self) -> list[dict]:
        return [{"slug": v["slug"], "url": v["url"], "clicks": v["clicks"],
                 "short_url": f"{self._base}/{v['slug']}"} for v in self._links.values()]
