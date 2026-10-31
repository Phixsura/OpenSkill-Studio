"""Sitemap generator — produce XML sitemap entries for marketplace SEO."""

from datetime import datetime, timezone


def generate_sitemap_entries(*, apps: list[dict], developers: list[dict],
                               collections: list[dict], base_url: str = "https://openskill.dev") -> list[dict]:
    entries = []
    entries.append({"loc": f"{base_url}/marketplace", "priority": "1.0", "changefreq": "daily"})
    for app in apps:
        if app.get("status") == "published":
            entries.append({
                "loc": f"{base_url}/marketplace/apps/{app['slug']}",
                "lastmod": app.get("updated_at", datetime.now(timezone.utc).isoformat()),
                "priority": "0.8", "changefreq": "weekly",
            })
    for dev in developers:
        entries.append({
            "loc": f"{base_url}/marketplace/developers/{dev['slug']}",
            "priority": "0.6", "changefreq": "monthly",
        })
    for col in collections:
        entries.append({
            "loc": f"{base_url}/marketplace/collections/{col['slug']}",
            "priority": "0.7", "changefreq": "weekly",
        })
    return entries


def render_sitemap_xml(*, entries: list[dict]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for e in entries:
        lines.append("  <url>")
        for k, v in e.items():
            lines.append(f"    <{k}>{v}</{k}>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines)
