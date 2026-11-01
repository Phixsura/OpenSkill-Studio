"""Landing page — the main OpenSkill landing page content."""

import html


def build_landing_page() -> dict:
    return {
        "hero": {
            "title": "Build, Publish, and Scale Apps",
            "subtitle": "The complete developer platform for creating marketplace apps",
            "cta_primary": {"label": "Get Started Free", "href": "/signup"},
            "cta_secondary": {"label": "View Docs", "href": "/docs"},
        },
        "features": [
            {"icon": "📦", "title": "App Marketplace", "description": "Publish and discover apps in our marketplace"},
            {"icon": "🔗", "title": "Webhooks & APIs", "description": "Real-time event delivery and REST APIs"},
            {"icon": "🔒", "title": "Enterprise Security", "description": "SSO, 2FA, audit logs, and compliance"},
            {"icon": "📊", "title": "Analytics", "description": "Real-time usage analytics and insights"},
            {"icon": "🚀", "title": "One-Click Deploy", "description": "Deploy to any environment instantly"},
            {"icon": "👥", "title": "Team Collaboration", "description": "Invite your team with role-based access"},
        ],
        "stats": [
            {"value": "5,000+", "label": "Apps Published"},
            {"value": "2,000+", "label": "Developers"},
            {"value": "12M+", "label": "API Calls/Month"},
            {"value": "99.99%", "label": "Uptime"},
        ],
        "testimonials": [
            {"quote": "The best developer platform I've ever used.", "author": "Alice Chen", "role": "CTO, Acme Corp"},
            {"quote": "Shipped our integration in half the time.", "author": "Bob Smith", "role": "Lead Engineer, StartupX"},
        ],
    }
