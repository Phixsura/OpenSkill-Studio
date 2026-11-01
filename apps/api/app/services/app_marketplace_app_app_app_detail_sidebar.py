"""App detail sidebar — metadata sidebar for app detail pages."""

import html
from datetime import datetime
from urllib.parse import urlparse


def _safe_url(url: str) -> str | None:
    try:
        p = urlparse(url)
        if p.scheme in ("http", "https") and p.hostname:
            return url
        return None
    except Exception:
        return None


def build_app_sidebar(*, app: dict) -> dict:
    info_items = [
        {"label": "Version", "value": app.get("version", "—"), "icon": "📦"},
        {"label": "Category", "value": app.get("category", "—"), "icon": "📂"},
        {"label": "Size", "value": app.get("size", "—"), "icon": "💾"},
        {"label": "Last Updated", "value": app.get("updated_at", "—")[:10] if app.get("updated_at") else "—", "icon": "📅"},
        {"label": "License", "value": app.get("license", "MIT"), "icon": "📄"},
        {"label": "Min SDK", "value": app.get("min_sdk", "—"), "icon": "🔧"},
    ]
    links = []
    for label, key, icon in [("Website", "website", "🌐"), ("Documentation", "docs_url", "📚"),
                               ("Source Code", "source_url", "💻")]:
        url = _safe_url(app.get(key, "") or "")
        if url:
            links.append({"label": label, "url": url, "icon": icon})
    if app.get("support_email"):
        mailto = f"mailto:{html.escape(app['support_email'])}"
        links.append({"label": "Support", "url": mailto, "icon": "💬"})
    return {"info_items": info_items, "links": links,
            "permissions": app.get("permissions", []),
            "tags": app.get("tags", [])}
