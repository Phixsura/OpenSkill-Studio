"""Coming soon page — pre-launch page for upcoming platform features."""


def build_coming_soon_page(*, feature_name: str, description: str, eta: str,
                               waitlist_count: int = 0) -> dict:
    return {
        "page_type": "coming_soon",
        "feature": feature_name,
        "description": description,
        "eta": eta,
        "waitlist": {"count": waitlist_count, "enabled": True},
        "social_proof": f"{waitlist_count:,} developers on the waitlist" if waitlist_count > 0 else None,
        "cta": {"label": "Join Waitlist", "action": "join_waitlist"},
    }


def add_to_waitlist(*, email: str, feature: str) -> dict:
    if not email or "@" not in email:
        return {"success": False, "error": "Invalid email"}
    return {"success": True, "email": email, "feature": feature,
            "message": "You're on the list! We'll notify you when it launches."}
