"""Sitemap FINAL — complete sitemap for the entire marketplace platform."""


def build_complete_sitemap(*, apps: list[dict], developers: list[dict], collections: list[dict],
                               categories: list[dict], blog_posts: list[dict],
                               base_url: str = "https://openskill.dev") -> dict:
    urls = []
    # Static pages
    static = ["/marketplace", "/marketplace/search", "/marketplace/collections",
              "/marketplace/trending", "/pricing", "/about", "/contact", "/blog",
              "/docs", "/docs/api", "/community", "/changelog", "/status", "/roadmap",
              "/terms", "/privacy", "/developer"]
    for path in static:
        urls.append({"loc": f"{base_url}{path}", "priority": "0.8", "changefreq": "weekly"})
    # Dynamic: apps
    for app in apps:
        if app.get("status") == "published":
            urls.append({"loc": f"{base_url}/marketplace/apps/{app.get('slug', '')}",
                          "priority": "0.7", "changefreq": "weekly"})
    # Dynamic: developers
    for dev in developers:
        urls.append({"loc": f"{base_url}/marketplace/developers/{dev.get('slug', '')}",
                      "priority": "0.6", "changefreq": "monthly"})
    # Dynamic: collections
    for col in collections:
        urls.append({"loc": f"{base_url}/marketplace/collections/{col.get('slug', '')}",
                      "priority": "0.6", "changefreq": "weekly"})
    # Dynamic: categories
    for cat in categories:
        urls.append({"loc": f"{base_url}/marketplace/category/{cat.get('id', '')}",
                      "priority": "0.7", "changefreq": "weekly"})
    # Dynamic: blog
    for post in blog_posts:
        urls.append({"loc": f"{base_url}/blog/{post.get('slug', '')}",
                      "priority": "0.5", "changefreq": "monthly"})
    return {"urls": urls, "total": len(urls), "static_count": len(static),
            "dynamic_count": len(urls) - len(static)}
