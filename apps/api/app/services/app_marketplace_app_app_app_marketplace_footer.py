"""App marketplace footer — marketplace-specific footer with links."""

import html
from datetime import datetime, timezone

FOOTER_SECTIONS = {
    "Marketplace": [
        {"label": "Browse Apps", "href": "/marketplace"},
        {"label": "Categories", "href": "/categories"},
        {"label": "Trending", "href": "/trending"},
        {"label": "Collections", "href": "/collections"},
    ],
    "Developers": [
        {"label": "Getting Started", "href": "/docs/quickstart"},
        {"label": "API Reference", "href": "/docs/api"},
        {"label": "SDK", "href": "/sdks"},
        {"label": "CLI", "href": "/cli"},
    ],
    "Support": [
        {"label": "Help Center", "href": "/help"},
        {"label": "Status", "href": "/status"},
        {"label": "Contact", "href": "/contact"},
    ],
    "Legal": [
        {"label": "Terms", "href": "/terms"},
        {"label": "Privacy", "href": "/privacy"},
        {"label": "Cookies", "href": "/cookies"},
    ],
}


def build_marketplace_footer(*, year: int | None = None) -> dict:
    y = year or datetime.now(timezone.utc).year
    sections = {name: [{"label": html.escape(l["label"]), "href": l["href"]} for l in links]
                for name, links in FOOTER_SECTIONS.items()}
    total_links = sum(len(v) for v in sections.values())
    return {"sections": sections, "section_count": len(sections),
            "total_links": total_links,
            "copyright": f"© {y} OpenSkill. All rights reserved.",
            "social": [
                {"name": "GitHub", "href": "https://github.com/openskill", "icon": "🐙"},
                {"name": "Twitter", "href": "https://twitter.com/openskill", "icon": "🐦"},
                {"name": "Discord", "href": "https://discord.gg/openskill", "icon": "💬"},
            ]}
