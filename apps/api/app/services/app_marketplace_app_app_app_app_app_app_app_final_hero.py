"""Marketplace final hero page — the definitive platform landing section."""
from __future__ import annotations


def build_hero_page() -> dict:
    return {
        "headline": "Build, Ship, and Scale Developer Apps",
        "subheadline": "The complete platform for marketplace integrations, APIs, and developer tools",
        "stats": [
            {"label": "Apps", "value": "500+", "icon": "📱"},
            {"label": "Developers", "value": "200+", "icon": "👩‍💻"},
            {"label": "API Calls/day", "value": "50M+", "icon": "📡"},
            {"label": "Uptime", "value": "99.99%", "icon": "🟢"},
        ],
        "features": [
            {"title": "Marketplace", "description": "Discover and install apps", "icon": "🏪"},
            {"title": "Developer Portal", "description": "SDK docs and guides", "icon": "📚"},
            {"title": "Webhooks", "description": "Real-time event delivery", "icon": "🔗"},
            {"title": "Analytics", "description": "Usage insights and metrics", "icon": "📊"},
            {"title": "Security", "description": "SOC2, GDPR, SSO", "icon": "🔒"},
            {"title": "Automation", "description": "CI/CD and workflows", "icon": "⚙️"},
        ],
        "cta": {"primary": "Start Building", "secondary": "View Documentation"},
        "trust": {"rating": "4.8 ⭐", "reviews": "15K+", "installs": "2.5M+"},
    }
