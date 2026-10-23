"""Sitemap generator — generate XML sitemaps for app pages."""

from xml.sax.saxutils import escape
from datetime import datetime


def generate_sitemap(*, base_url: str, pages: list[dict]) -> dict:
    safe_base = escape(base_url.rstrip("/"))
    urls = []
    for page in pages:
        loc = f"{safe_base}/{escape(page['path'].lstrip('/'))}"
        entry = f"  <url>\n    <loc>{loc}</loc>"
        if page.get("lastmod"):
            entry += f"\n    <lastmod>{escape(page['lastmod'])}</lastmod>"
        priority = page.get("priority", 0.5)
        entry += f"\n    <priority>{priority}</priority>"
        entry += "\n  </url>"
        urls.append(entry)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n"
        '</urlset>'
    )
    return {"xml": xml, "url_count": len(pages), "content_type": "application/xml"}
