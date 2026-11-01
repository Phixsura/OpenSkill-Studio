"""Marketplace Sitemap — generate XML sitemaps for SEO."""
from __future__ import annotations
import html
import time


class MktplaceSitemapService:
    BASE_URL = "https://marketplace.openskill.dev"

    def __init__(self):
        self._urls: list[dict] = []

    def add(self, path: str, priority: float = 0.5, changefreq: str = "weekly") -> None:
        self._urls.append({"path": path, "priority": priority,
                           "changefreq": changefreq, "lastmod": time.strftime("%Y-%m-%d")})

    def generate_xml(self) -> str:
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for u in self._urls:
            loc = html.escape(f"{self.BASE_URL}{u['path']}")
            lines.append(f"  <url><loc>{loc}</loc><lastmod>{u['lastmod']}</lastmod>"
                         f"<changefreq>{u['changefreq']}</changefreq>"
                         f"<priority>{u['priority']}</priority></url>")
        lines.append("</urlset>")
        return "\n".join(lines)

    def add_extensions(self, extension_ids: list[str]) -> int:
        for eid in extension_ids:
            self.add(f"/ext/{eid}", 0.8, "daily")
        return len(extension_ids)

    def add_categories(self, categories: list[str]) -> int:
        for cat in categories:
            self.add(f"/category/{cat}", 0.6, "weekly")
        return len(categories)

    def count(self) -> int:
        return len(self._urls)
