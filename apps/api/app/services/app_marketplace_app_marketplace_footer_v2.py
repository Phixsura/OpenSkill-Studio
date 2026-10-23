"""Marketplace footer v2 — rich footer with newsletter signup and social proof."""


def build_footer_v2(*, stats: dict, newsletter_enabled: bool = True,
                       social_links: dict | None = None) -> dict:
    columns = [
        {"title": "Product", "links": [
            {"label": "Marketplace", "url": "/marketplace"}, {"label": "Pricing", "url": "/pricing"},
            {"label": "Enterprise", "url": "/enterprise"}, {"label": "Changelog", "url": "/changelog"},
        ]},
        {"title": "Developers", "links": [
            {"label": "Documentation", "url": "/docs"}, {"label": "API Reference", "url": "/docs/api"},
            {"label": "SDKs", "url": "/docs/sdks"}, {"label": "Community", "url": "/community"},
        ]},
        {"title": "Company", "links": [
            {"label": "About", "url": "/about"}, {"label": "Blog", "url": "/blog"},
            {"label": "Careers", "url": "/careers"}, {"label": "Contact", "url": "/contact"},
        ]},
        {"title": "Legal", "links": [
            {"label": "Terms of Service", "url": "/terms"}, {"label": "Privacy Policy", "url": "/privacy"},
            {"label": "Cookie Policy", "url": "/cookies"}, {"label": "Security", "url": "/security"},
        ]},
    ]
    return {"columns": columns, "newsletter": {"enabled": newsletter_enabled},
            "social": social_links or {"twitter": "#", "github": "#", "linkedin": "#"},
            "stats_text": f"Trusted by {stats.get('developers', 0):,} developers worldwide",
            "copyright": f"© 2026 OpenSkill. All rights reserved."}
