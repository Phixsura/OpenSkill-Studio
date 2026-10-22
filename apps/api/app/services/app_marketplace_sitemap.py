"""Marketplace sitemap — generate sitemap for SEO."""

from datetime import UTC, datetime


def generate_sitemap(apps: list[dict], *, base_url: str = "https://marketplace.openskill.studio") -> str:
    urls = [f'  <url><loc>{base_url}/apps/{a.get("slug")}</loc><lastmod>{a.get("updated_at", datetime.now(UTC).strftime("%Y-%m-%d"))}</lastmod></url>' for a in apps]
    devs = set()
    for a in apps:
        if a.get("developer_slug"):
            devs.add(a["developer_slug"])
    dev_urls = [f'  <url><loc>{base_url}/developers/{slug}</loc></url>' for slug in sorted(devs)]
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{base_url}</loc></url>
  <url><loc>{base_url}/apps</loc></url>
  <url><loc>{base_url}/categories</loc></url>
{chr(10).join(urls)}
{chr(10).join(dev_urls)}
</urlset>'''
