"""Social share builder — generate share links and open graph meta for apps."""
from __future__ import annotations
import html
from urllib.parse import quote


def build_share_links(*, title: str, url: str, description: str = "") -> dict:
    safe_title = quote(title)
    safe_url = quote(url)
    safe_desc = quote(description[:200])
    return {
        "twitter": f"https://twitter.com/intent/tweet?text={safe_title}&url={safe_url}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={safe_url}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={safe_url}",
        "email": f"mailto:?subject={safe_title}&body={safe_desc}%0A{safe_url}",
        "copy_url": url,
    }


def build_og_meta(*, title: str, description: str, image: str = "",
                     app_type: str = "website", url: str = "") -> dict:
    return {
        "og:title": html.escape(title),
        "og:description": html.escape(description[:200]),
        "og:image": image,
        "og:type": app_type,
        "og:url": url,
        "twitter:card": "summary_large_image" if image else "summary",
    }
