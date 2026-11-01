"""Landing page hero — dynamic hero section content for the platform."""
from __future__ import annotations
import html


def build_hero(*, headline: str, subheadline: str, cta_primary: str = "Get Started",
                cta_secondary: str = "View Docs", stats: dict | None = None) -> dict:
    default_stats = {"apps": "500+", "developers": "200+", "api_calls": "50M+"}
    return {
        "headline": html.escape(headline),
        "subheadline": html.escape(subheadline),
        "cta_primary": cta_primary,
        "cta_secondary": cta_secondary,
        "stats": stats or default_stats,
        "social_proof": [
            {"name": "GitHub", "icon": "⭐", "value": "5K+ stars"},
            {"name": "Discord", "icon": "💬", "value": "3.5K members"},
            {"name": "NPM", "icon": "📦", "value": "100K+ downloads"},
        ],
    }
