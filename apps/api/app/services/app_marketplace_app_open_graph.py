"""Open Graph — generate social sharing metadata for apps."""

import html


def generate_og_tags(*, app_name: str, description: str, image_url: str | None = None,
                       url: str, app_type: str = "app") -> dict:
    safe_name = html.escape(app_name[:70])
    safe_desc = html.escape(description[:200])
    safe_url = html.escape(url)
    tags = {
        "og:title": safe_name,
        "og:description": safe_desc,
        "og:url": safe_url,
        "og:type": "website",
        "og:site_name": "OpenSkill Marketplace",
        "twitter:card": "summary_large_image",
        "twitter:title": safe_name,
        "twitter:description": safe_desc,
    }
    if image_url:
        safe_img = html.escape(image_url)
        tags["og:image"] = safe_img
        tags["twitter:image"] = safe_img
    return {"tags": tags, "meta_html": _render_meta(tags)}


def _render_meta(tags: dict) -> str:
    lines = []
    for key, value in tags.items():
        prop = "name" if key.startswith("twitter:") else "property"
        lines.append(f'<meta {prop}="{key}" content="{value}" />')
    return "\n".join(lines)
