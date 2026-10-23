"""Share page — shareable app profiles with social preview and embed options."""

from html import escape
from urllib.parse import quote, urlencode


def build_share_page(*, app: dict, base_url: str = "https://openskill.dev") -> dict:
    slug = quote(str(app.get("slug", app.get("id", ""))), safe="")
    name = str(app.get("name", ""))
    url = f"{base_url}/marketplace/apps/{slug}"
    text = f"Check out {name} on OpenSkill Marketplace"
    return {
        "page_type": "share",
        "app": {"name": name, "slug": slug, "description": app.get("description", "")[:200],
                "category": app.get("category"), "rating": app.get("avg_rating", 0),
                "installs": app.get("install_count", 0)},
        "url": url,
        "social": {
            "twitter": f"https://twitter.com/intent/tweet?{urlencode({'text': text, 'url': url})}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?{urlencode({'url': url})}",
        },
        "embed": {
            "badge": f'<a href="{escape(url, quote=True)}"><img src="{escape(base_url, quote=True)}/badge/{slug}.svg" alt="{escape(name, quote=True)}" /></a>',
            "button": f'<a href="{escape(url, quote=True)}" style="padding:8px 16px;background:#2563eb;color:#fff;border-radius:6px;text-decoration:none">Install {escape(name, quote=True)}</a>',
        },
        "qr_url": f"{base_url}/qr/{slug}.png",
        "og": {"title": name, "description": app.get("description", "")[:160], "image": app.get("icon"), "url": url},
    }
