"""User consent — manage granular data collection consent."""

from datetime import datetime


CONSENT_CATEGORIES = {
    "essential": {"label": "Essential", "required": True, "description": "Required for basic functionality"},
    "analytics": {"label": "Analytics", "required": False, "description": "Usage statistics and analytics"},
    "marketing": {"label": "Marketing", "required": False, "description": "Promotional emails and ads"},
    "personalization": {"label": "Personalization", "required": False, "description": "Customized experience"},
    "third_party": {"label": "Third-party sharing", "required": False, "description": "Data shared with partners"},
}


def get_consent_options() -> dict:
    return {
        "categories": [{"id": k, **v} for k, v in CONSENT_CATEGORIES.items()],
        "total": len(CONSENT_CATEGORIES),
    }


def save_consent(*, user_id: str, choices: dict[str, bool]) -> dict:
    saved = {}
    for cat_id, info in CONSENT_CATEGORIES.items():
        if info["required"]:
            saved[cat_id] = True  # can't opt out of essential
        else:
            saved[cat_id] = choices.get(cat_id, False)
    return {
        "user_id": user_id,
        "consent": saved,
        "consented_at": datetime.utcnow().isoformat(),
        "essential_forced": True,
        "optional_accepted": sum(1 for k, v in saved.items() if v and not CONSENT_CATEGORIES[k]["required"]),
    }
