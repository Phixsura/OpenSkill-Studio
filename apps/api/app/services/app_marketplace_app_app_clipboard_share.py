"""Clipboard share — generate shareable links and embed codes."""

import html
from urllib.parse import urlparse, quote


def _safe_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return ""
    return url


def build_share_options(*, app_name: str, app_url: str, description: str = "") -> dict:
    safe = _safe_url(app_url)
    if not safe:
        return {"error": "Invalid URL scheme"}
    name_esc = html.escape(app_name)
    desc_esc = html.escape(description)
    encoded_url = quote(safe, safe="/:?=&")
    encoded_text = quote(f"Check out {app_name} — {description}")
    return {
        "direct_link": safe,
        "markdown": f"[{name_esc}]({safe})",
        "html_link": f'<a href="{html.escape(safe)}">{name_esc}</a>',
        "twitter": f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}",
        "embed_iframe": f'<iframe src="{html.escape(safe)}" width="600" height="400" title="{name_esc}"></iframe>',
        "badge": f"[![{name_esc}](https://img.shields.io/badge/OpenSkill-{quote(app_name)}-blue)]({safe})",
    }
