"""Sitemap generator — XML sitemap builder for marketplace apps."""

import html
from datetime import datetime, timezone
from urllib.parse import urlparse


def generate_sitemap(*, base_url: str, pages: list[dict]) -> dict:
    parsed = urlparse(base_url)
    if parsed.scheme not in ("https", "http"):
        return {"error": "Invalid base URL"}
    entries = []
    for p in pages:
        path = p.get("path", "/")
        url = f"{base_url.rstrip('/')}{path}"
        entries.append({
            "url": url,
            "lastmod": p.get("lastmod", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "changefreq": p.get("changefreq", "weekly"),
            "priority": p.get("priority", 0.5),
        })
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for e in entries:
        xml_lines.append(f"  <url><loc>{html.escape(e['url'])}</loc>"
                         f"<lastmod>{e['lastmod']}</lastmod>"
                         f"<changefreq>{e['changefreq']}</changefreq>"
                         f"<priority>{e['priority']}</priority></url>")
    xml_lines.append("</urlset>")
    xml = "\n".join(xml_lines)
    return {"xml": xml, "url_count": len(entries), "size_bytes": len(xml.encode())}
