"""Landing page data — comprehensive data for the platform landing page."""
from __future__ import annotations


def build_landing_page_data() -> dict:
    return {
        "hero": {
            "headline": "The Developer Platform for Modern Apps",
            "subheadline": "Build, ship, and scale integrations with the OpenSkill marketplace",
            "cta_primary": "Start Free", "cta_secondary": "View Docs",
        },
        "stats": {"apps": "500+", "developers": "200+", "api_calls": "50M+/day", "uptime": "99.99%"},
        "features": [
            {"icon": "🏪", "title": "Marketplace", "desc": "Discover and install 500+ apps"},
            {"icon": "📡", "title": "Powerful API", "desc": "RESTful API with webhooks"},
            {"icon": "📦", "title": "SDKs", "desc": "TypeScript, Python, Go, Java, Ruby"},
            {"icon": "🔒", "title": "Enterprise Security", "desc": "SOC2, GDPR, SSO, RBAC"},
            {"icon": "📊", "title": "Analytics", "desc": "Real-time usage insights"},
            {"icon": "🚀", "title": "CI/CD", "desc": "Deploy with one click"},
        ],
        "testimonials": [
            {"quote": "Saved us months of development time", "author": "CTO, TechCorp", "rating": 5},
            {"quote": "The best developer experience I've used", "author": "Lead Dev, StartupXY", "rating": 5},
        ],
        "pricing_cta": {"title": "Start building for free", "subtitle": "No credit card required"},
    }
