"""Global navigation — build the main platform navigation with mega menu."""
from __future__ import annotations

NAV_SECTIONS = {
    "marketplace": {"label": "Marketplace", "icon": "🏪", "items": [
        {"label": "Browse Apps", "path": "/marketplace", "icon": "📱"},
        {"label": "Categories", "path": "/marketplace/categories", "icon": "📦"},
        {"label": "Trending", "path": "/marketplace/trending", "icon": "🔥"},
        {"label": "Collections", "path": "/marketplace/collections", "icon": "📚"},
    ]},
    "develop": {"label": "Develop", "icon": "💻", "items": [
        {"label": "Dashboard", "path": "/dashboard", "icon": "🏠"},
        {"label": "Apps", "path": "/apps", "icon": "📱"},
        {"label": "API Keys", "path": "/settings/keys", "icon": "🔑"},
        {"label": "Webhooks", "path": "/webhooks", "icon": "🔗"},
        {"label": "Analytics", "path": "/analytics", "icon": "📊"},
    ]},
    "docs": {"label": "Docs", "icon": "📚", "items": [
        {"label": "Getting Started", "path": "/docs/getting-started", "icon": "🚀"},
        {"label": "API Reference", "path": "/docs/api", "icon": "📡"},
        {"label": "SDKs", "path": "/docs/sdks", "icon": "📦"},
        {"label": "Guides", "path": "/docs/guides", "icon": "📖"},
    ]},
    "community": {"label": "Community", "icon": "🌍", "items": [
        {"label": "Forum", "path": "/community/forum", "icon": "💬"},
        {"label": "Blog", "path": "/blog", "icon": "📝"},
        {"label": "Events", "path": "/events", "icon": "📅"},
        {"label": "Showcase", "path": "/showcase", "icon": "🏆"},
    ]},
}


def build_global_nav(*, active_section: str = "") -> dict:
    sections = []
    for sid, section in NAV_SECTIONS.items():
        sections.append({"id": sid, **section, "active": sid == active_section})
    return {"sections": sections, "total_links": sum(len(s["items"]) for s in NAV_SECTIONS.values())}


def get_section_items(section_id: str) -> list[dict]:
    section = NAV_SECTIONS.get(section_id)
    return section["items"] if section else []
