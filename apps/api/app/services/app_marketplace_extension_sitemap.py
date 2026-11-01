"""Marketplace Sitemap — generate sitemaps for marketplace SEO.

Builds XML sitemaps with extension pages, category pages, developer
profiles, and documentation with change frequency and priority.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SitemapEntry:
    url: str
    changefreq: str = "weekly"  # always, hourly, daily, weekly, monthly, yearly
    priority: float = 0.5
    lastmod: str = ""


class MarketplaceSitemapService:
    """Generates marketplace sitemaps for SEO."""

    BASE_URL = "https://marketplace.openskill.dev"

    def __init__(self):
        self._entries: list[SitemapEntry] = []

    def add_extensions(self, extensions: list[dict]) -> int:
        for ext in extensions:
            self._entries.append(SitemapEntry(
                url=f"{self.BASE_URL}/ext/{ext['id']}",
                changefreq="weekly", priority=0.8,
                lastmod=ext.get("updated", ""),
            ))
        return len(extensions)

    def add_categories(self, categories: list[str]) -> int:
        for cat in categories:
            self._entries.append(SitemapEntry(
                url=f"{self.BASE_URL}/category/{cat}",
                changefreq="daily", priority=0.7,
            ))
        return len(categories)

    def add_developers(self, developers: list[dict]) -> int:
        for dev in developers:
            self._entries.append(SitemapEntry(
                url=f"{self.BASE_URL}/developer/{dev['id']}",
                changefreq="monthly", priority=0.5,
            ))
        return len(developers)

    def add_docs(self, docs: list[dict]) -> int:
        for doc in docs:
            self._entries.append(SitemapEntry(
                url=f"{self.BASE_URL}/docs/{doc['slug']}",
                changefreq="monthly", priority=0.6,
            ))
        return len(docs)

    def generate_xml(self) -> str:
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        # Add homepage
        lines.append(f'  <url><loc>{self.BASE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>')
        for entry in self._entries:
            parts = [f'    <loc>{entry.url}</loc>',
                     f'    <changefreq>{entry.changefreq}</changefreq>',
                     f'    <priority>{entry.priority}</priority>']
            if entry.lastmod:
                parts.append(f'    <lastmod>{entry.lastmod}</lastmod>')
            lines.append(f'  <url>\n' + '\n'.join(parts) + '\n  </url>')
        lines.append('</urlset>')
        return '\n'.join(lines)

    def get_stats(self) -> dict:
        return {"total_urls": len(self._entries) + 1,  # +1 for homepage
                "extensions": sum(1 for e in self._entries if "/ext/" in e.url),
                "categories": sum(1 for e in self._entries if "/category/" in e.url),
                "developers": sum(1 for e in self._entries if "/developer/" in e.url),
                "docs": sum(1 for e in self._entries if "/docs/" in e.url)}
