"""Final app page builder — assemble all sections for a complete app page."""
from __future__ import annotations
import html


def build_complete_app_page(app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    return {
        "hero": {"name": name, "icon": app.get("icon", "📱"),
                  "tagline": html.escape(app.get("tagline", "")[:100]),
                  "developer": html.escape(app.get("developer", "")),
                  "rating": app.get("rating", 0), "installs": app.get("installs", 0),
                  "verified": app.get("verified", False)},
        "tabs": [
            {"id": "overview", "label": "Overview", "icon": "📋"},
            {"id": "reviews", "label": "Reviews", "icon": "⭐"},
            {"id": "changelog", "label": "Changelog", "icon": "📝"},
            {"id": "privacy", "label": "Privacy", "icon": "🔒"},
            {"id": "support", "label": "Support", "icon": "💬"},
        ],
        "sidebar": {
            "install_button": True,
            "price_display": "Free" if app.get("price_type") == "free" else f"${app.get('price', 0)}/mo",
            "links": [
                {"label": "Documentation", "url": app.get("docs_url", "")},
                {"label": "Report Issue", "url": ""},
                {"label": "Share", "url": ""},
            ],
        },
        "meta": {"version": app.get("version", ""), "updated": app.get("updated", ""),
                  "category": app.get("category", ""), "size": app.get("size", "")},
    }
