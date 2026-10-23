"""Cookie consent — manage cookie preferences for marketplace users."""

COOKIE_CATEGORIES = {
    "essential": {"label": "Essential", "required": True, "description": "Required for basic functionality"},
    "analytics": {"label": "Analytics", "required": False, "description": "Help us improve with usage data"},
    "marketing": {"label": "Marketing", "required": False, "description": "Personalized recommendations"},
    "preferences": {"label": "Preferences", "required": False, "description": "Remember your settings"},
}


def get_cookie_config() -> dict:
    return {"categories": COOKIE_CATEGORIES, "version": "1.0",
            "privacy_url": "/privacy", "cookie_policy_url": "/cookies"}


def save_consent(*, user_id: str | None, consent: dict[str, bool]) -> dict:
    final = {"essential": True}
    for cat in COOKIE_CATEGORIES:
        if COOKIE_CATEGORIES[cat]["required"]:
            final[cat] = True
        else:
            final[cat] = consent.get(cat, False)
    return {"consent": final, "user_id": user_id, "version": "1.0"}


def check_consent(*, consent: dict, category: str) -> bool:
    if COOKIE_CATEGORIES.get(category, {}).get("required"):
        return True
    return consent.get(category, False)
