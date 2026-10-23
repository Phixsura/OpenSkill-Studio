"""Platform footer — generate footer content for the marketplace."""


def build_footer(*, year: int = 2026) -> dict:
    return {
        "brand": {"name": "OpenSkill", "tagline": "The Developer Platform"},
        "sections": [
            {"title": "Product", "links": [
                {"label": "Marketplace", "url": "/marketplace"},
                {"label": "SDKs", "url": "/sdks"},
                {"label": "Pricing", "url": "/pricing"},
                {"label": "Changelog", "url": "/changelog"},
            ]},
            {"title": "Developers", "links": [
                {"label": "Documentation", "url": "/docs"},
                {"label": "API Reference", "url": "/docs/api"},
                {"label": "Community", "url": "/community"},
                {"label": "Blog", "url": "/blog"},
            ]},
            {"title": "Company", "links": [
                {"label": "About", "url": "/about"},
                {"label": "Careers", "url": "/careers"},
                {"label": "Privacy", "url": "/privacy"},
                {"label": "Terms", "url": "/terms"},
            ]},
        ],
        "social": [
            {"platform": "twitter", "url": "https://twitter.com/openskill", "icon": "𝕏"},
            {"platform": "github", "url": "https://github.com/openskill", "icon": "🐙"},
            {"platform": "discord", "url": "https://discord.gg/openskill", "icon": "💬"},
        ],
        "copyright": f"© {year} OpenSkill. All rights reserved.",
    }
