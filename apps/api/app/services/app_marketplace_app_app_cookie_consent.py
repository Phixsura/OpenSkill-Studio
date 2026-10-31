"""Cookie consent — cookie policy builder with category management."""

import html
import secrets
from datetime import datetime, timezone

CATEGORIES = {
    "necessary": {"label": "Necessary", "required": True, "description": "Essential for the site to function"},
    "functional": {"label": "Functional", "required": False, "description": "Enhanced functionality and personalization"},
    "analytics": {"label": "Analytics", "required": False, "description": "Help us understand how visitors use the site"},
    "advertising": {"label": "Advertising", "required": False, "description": "Used for targeted advertising"},
}


def build_cookie_policy(*, domain: str, current_consent: dict[str, bool] | None = None) -> dict:
    items = []
    for cat_id, info in CATEGORIES.items():
        consent = current_consent.get(cat_id, info["required"]) if current_consent else info["required"]
        items.append({"id": cat_id, "label": info["label"], "required": info["required"],
                       "description": info["description"], "consented": consent})
    return {"domain": html.escape(domain), "categories": items,
            "total": len(items), "all_accepted": all(i["consented"] for i in items)}


def save_consent(*, user_id: str, consents: dict[str, bool]) -> dict:
    final = {}
    for cat_id, info in CATEGORIES.items():
        final[cat_id] = True if info["required"] else consents.get(cat_id, False)
    return {"consent_id": f"cc_{secrets.token_hex(6)}", "user_id": user_id,
            "consents": final, "saved_at": datetime.now(timezone.utc).isoformat()}
