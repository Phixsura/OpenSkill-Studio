"""Home banner — seasonal and promotional banners for the marketplace."""
from __future__ import annotations
import html


BANNERS = [
    {"id": "devcon", "title": "DevCon 2026", "body": "Join us for the biggest developer conference", "cta": "Register Now",
     "gradient": "from-purple-600 to-indigo-600", "icon": "🎪", "active": True},
    {"id": "hackathon", "title": "Build & Win", "body": "Submit your app for a chance to win $10K", "cta": "Enter Hackathon",
     "gradient": "from-green-600 to-teal-600", "icon": "🏆", "active": True},
    {"id": "launch", "title": "Platform v4.0", "body": "GraphQL API, SSO, and 50+ new features", "cta": "See What's New",
     "gradient": "from-blue-600 to-cyan-600", "icon": "🚀", "active": True},
]


def get_active_banners() -> list[dict]:
    return [{"id": b["id"], "title": b["title"], "body": b["body"],
             "cta": b["cta"], "gradient": b["gradient"], "icon": b["icon"]}
            for b in BANNERS if b["active"]]


def get_banner(banner_id: str) -> dict | None:
    return next((b for b in BANNERS if b["id"] == banner_id), None)
