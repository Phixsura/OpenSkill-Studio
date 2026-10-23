"""App sharing — generate shareable links and previews for marketplace apps."""
from __future__ import annotations
import html
from urllib.parse import quote


def build_share_preview(app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    desc = html.escape(app.get("description", "")[:160])
    app_url = f"https://marketplace.openskill.io/apps/{quote(app.get('id', ''))}"
    return {
        "title": f"{name} — OpenSkill Marketplace",
        "description": desc,
        "url": app_url,
        "image": app.get("og_image", f"https://marketplace.openskill.io/og/{app.get('id', '')}.png"),
        "share_links": {
            "twitter": f"https://twitter.com/intent/tweet?text={quote(name)}&url={quote(app_url)}",
            "linkedin": f"https://linkedin.com/sharing/share-offsite/?url={quote(app_url)}",
            "copy": app_url,
        },
    }
