"""Cookie consent manager — GDPR-compliant cookie preferences."""
from __future__ import annotations

COOKIE_CATEGORIES = {
    "necessary": {"label": "Necessary", "description": "Essential for the site to function.", "required": True, "default": True},
    "analytics": {"label": "Analytics", "description": "Help us understand how you use the site.", "required": False, "default": False},
    "marketing": {"label": "Marketing", "description": "Used for targeted advertising.", "required": False, "default": False},
    "preferences": {"label": "Preferences", "description": "Remember your settings.", "required": False, "default": True},
}


def get_consent_options() -> list[dict]:
    return [{"id": k, **v} for k, v in COOKIE_CATEGORIES.items()]


def process_consent(choices: dict[str, bool]) -> dict:
    result = {}
    for cat_id, info in COOKIE_CATEGORIES.items():
        if info["required"]:
            result[cat_id] = True  # Always enabled
        else:
            result[cat_id] = choices.get(cat_id, info["default"])
    accepted = [k for k, v in result.items() if v]
    rejected = [k for k, v in result.items() if not v]
    return {"consent": result, "accepted": accepted, "rejected": rejected,
            "all_accepted": len(rejected) == 0}
