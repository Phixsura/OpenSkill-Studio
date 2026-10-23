"""App detail sidebar — metadata sidebar for app detail pages."""

import html
from urllib.parse import urlparse


def _safe_url(url: str) -> str | None:
    """Only allow http/https URLs with a hostname."""
    try:
        p = urlparse(url)
        return url if p.scheme in ("http", "https") and p.hostname else None
    except Exception:
        return None

from datetime import datetime


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
    if app.get("website"):
        safe = _safe_url(app["website"])
    if safe:
        links.append({"label": "Website", "url": safe, "icon": "🌐"})
    if app.get("docs_url"):
        links.append({"label": "Documentation", "url": app["docs_url"], "icon": "📚"})
    if app.get("source_url"):
        links.append({"label": "Source Code", "url": app["source_url"], "icon": "💻"})
    if app.get("support_email"):
        links.append({"label": "Support", "url": f"mailto:{html.escape(app['support_email'])}", "icon": "💬"})
    return {"info_items": info_items, "links": links,
            "permissions": app.get("permissions", []),
            "tags": app.get("tags", [])}
