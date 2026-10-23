"""App store listing preview — preview how an app will appear in the marketplace."""
from __future__ import annotations
import html


def build_listing_preview(app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    return {
        "card_preview": {
            "name": name, "icon": app.get("icon", "📱"),
            "tagline": html.escape(app.get("tagline", "")[:80]),
            "rating": app.get("rating", 0),
            "installs_display": f"{app.get('installs', 0):,}",
            "price_display": "Free" if app.get("price_type") == "free" else f"${app.get('price', 0)}/mo",
            "verified": app.get("verified", False),
            "category": app.get("category", ""),
        },
        "completeness": _check_completeness(app),
    }


def _check_completeness(app: dict) -> dict:
    fields = {"name": bool(app.get("name")), "description": len(app.get("description", "")) >= 50,
              "icon": bool(app.get("icon")), "category": bool(app.get("category")),
              "screenshots": len(app.get("screenshots", [])) >= 1,
              "privacy_url": bool(app.get("privacy_url")),
              "tagline": bool(app.get("tagline"))}
    filled = sum(1 for v in fields.values() if v)
    return {"fields": fields, "filled": filled, "total": len(fields),
            "pct": round(filled / len(fields) * 100),
            "ready": all(fields.values())}
