"""Marketplace footer — build footer data with links, stats, and social."""


def build_marketplace_footer(*, stats: dict, social_links: dict | None = None) -> dict:
    return {
        "sections": [
            {"title": "Platform", "links": [
                {"label": "Marketplace", "url": "/marketplace"},
                {"label": "Developer Portal", "url": "/developer"},
                {"label": "Documentation", "url": "/docs"},
                {"label": "API Reference", "url": "/docs/api"},
            ]},
            {"title": "Company", "links": [
                {"label": "About", "url": "/about"},
                {"label": "Blog", "url": "/blog"},
                {"label": "Careers", "url": "/careers"},
                {"label": "Contact", "url": "/contact"},
            ]},
            {"title": "Legal", "links": [
                {"label": "Terms", "url": "/terms"},
                {"label": "Privacy", "url": "/privacy"},
                {"label": "Security", "url": "/security"},
            ]},
        ],
        "stats_bar": f"{stats.get('apps', 0)} apps · {stats.get('developers', 0)} developers",
        "social": social_links or {},
        "copyright": "OpenSkill",
    }
