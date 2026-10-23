"""OG meta — Open Graph and Twitter Card meta tag generator."""

import html
from urllib.parse import urlparse, quote


def build_og_meta(*, title: str, description: str, url: str,
                    image: str | None = None, site_name: str = "OpenSkill Marketplace",
                    type: str = "website") -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return {"error": "Invalid URL scheme"}
    tags = [
        {"property": "og:title", "content": html.escape(title)},
        {"property": "og:description", "content": html.escape(description[:200])},
        {"property": "og:url", "content": url},
        {"property": "og:site_name", "content": html.escape(site_name)},
        {"property": "og:type", "content": type},
        {"name": "twitter:card", "content": "summary_large_image" if image else "summary"},
        {"name": "twitter:title", "content": html.escape(title)},
        {"name": "twitter:description", "content": html.escape(description[:200])},
    ]
    if image:
        tags.append({"property": "og:image", "content": image})
        tags.append({"name": "twitter:image", "content": image})
    html_tags = "\n".join(
        f'<meta {"property" if "property" in t else "name"}="{t.get("property", t.get("name", ""))}" content="{t["content"]}" />'
        for t in tags)
    return {"tags": tags, "html": html_tags, "tag_count": len(tags)}
