"""Complete footer — the final footer with all sections, social, and legal."""

import html
from datetime import datetime, timezone


def build_complete_footer() -> dict:
    return {
        "brand": {"name": "OpenSkill", "tagline": "The Complete Developer Platform", "icon": "🧩"},
        "sections": {
            "Product": [
                {"label": "Marketplace", "href": "/marketplace"},
                {"label": "Pricing", "href": "/pricing"},
                {"label": "Features", "href": "/features"},
                {"label": "SDK", "href": "/sdk"},
            ],
            "Developers": [
                {"label": "Documentation", "href": "/docs"},
                {"label": "API Reference", "href": "/api"},
                {"label": "Changelog", "href": "/changelog"},
                {"label": "CLI", "href": "/cli"},
            ],
            "Company": [
                {"label": "About", "href": "/about"},
                {"label": "Blog", "href": "/blog"},
                {"label": "Careers", "href": "/careers"},
                {"label": "Contact", "href": "/contact"},
            ],
            "Legal": [
                {"label": "Terms of Service", "href": "/terms"},
                {"label": "Privacy Policy", "href": "/privacy"},
                {"label": "Cookie Policy", "href": "/cookies"},
                {"label": "DPA", "href": "/dpa"},
            ],
        },
        "social": [
            {"name": "GitHub", "icon": "🐙", "href": "https://github.com/openskill"},
            {"name": "Twitter", "icon": "🐦", "href": "https://twitter.com/openskill"},
            {"name": "Discord", "icon": "💬", "href": "https://discord.gg/openskill"},
            {"name": "LinkedIn", "icon": "💼", "href": "https://linkedin.com/company/openskill"},
        ],
        "copyright": f"© {datetime.now(timezone.utc).year} OpenSkill, Inc. All rights reserved.",
        "badges": [
            {"label": "SOC 2 Compliant", "icon": "🛡️"},
            {"label": "GDPR Ready", "icon": "🇪🇺"},
            {"label": "99.99% Uptime", "icon": "⬆️"},
        ],
    }
