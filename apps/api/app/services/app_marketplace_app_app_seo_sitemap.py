"""SEO sitemap — generate comprehensive sitemaps for marketplace pages."""

from xml.sax.saxutils import escape
from datetime import datetime


def generate_marketplace_sitemap(*, base_url: str, apps: list[dict],
                                    categories: list[dict], developers: list[dict]) -> dict:
    safe_base = escape(base_url.rstrip("/"))
    urls = []
    # Static pages
    static = ["/", "/apps", "/categories", "/developers", "/docs", "/pricing"]
    for path in static:
        urls.append({"loc": f"{safe_base}{path}", "priority": 0.8, "changefreq": "weekly"})
    # App pages
    for app in apps:
        urls.append({"loc": f"{safe_base}/apps/{escape(app['id'])}", "priority": 0.6,
                      "changefreq": "daily", "lastmod": app.get("updated_at")})
    # Category pages
    for cat in categories:
        urls.append({"loc": f"{safe_base}/categories/{escape(cat['id'])}", "priority": 0.5,
                      "changefreq": "weekly"})
    # Developer pages
    for dev in developers:
        urls.append({"loc": f"{safe_base}/developers/{escape(dev['id'])}", "priority": 0.4,
                      "changefreq": "monthly"})
    return {"urls": urls, "total_urls": len(urls),
            "static_pages": len(static), "dynamic_pages": len(urls) - len(static)}
