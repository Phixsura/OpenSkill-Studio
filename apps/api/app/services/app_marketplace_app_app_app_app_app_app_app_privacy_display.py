"""Privacy policy display — show app data practices and permissions."""
from __future__ import annotations
import html
from urllib.parse import urlparse

DATA_CATEGORIES = {
    "personal": {"icon": "👤", "label": "Personal Information", "risk": "high"},
    "usage": {"icon": "📊", "label": "Usage Analytics", "risk": "medium"},
    "device": {"icon": "📱", "label": "Device Information", "risk": "low"},
    "cookies": {"icon": "🍪", "label": "Cookies & Tracking", "risk": "medium"},
    "financial": {"icon": "💳", "label": "Financial Data", "risk": "critical"},
    "location": {"icon": "📍", "label": "Location Data", "risk": "high"},
}


def build_privacy_summary(app: dict) -> dict:
    data_collected = app.get("data_collected", [])
    items = []
    max_risk = "low"
    risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    for cat_id in data_collected:
        cat = DATA_CATEGORIES.get(cat_id, {"icon": "❓", "label": cat_id, "risk": "unknown"})
        items.append({"id": cat_id, **cat})
        if risk_order.get(cat["risk"], 0) > risk_order.get(max_risk, 0):
            max_risk = cat["risk"]
    # Validate privacy URL scheme
    privacy_raw = app.get("privacy_url", "")
    parsed = urlparse(privacy_raw)
    safe_privacy = privacy_raw if parsed.scheme in ("http", "https") and parsed.hostname else ""
    return {
        "app_name": html.escape(app.get("name", "")),
        "privacy_url": safe_privacy,
        "data_collected": items, "data_count": len(items),
        "max_risk": max_risk,
        "has_privacy_policy": bool(safe_privacy),
    }
