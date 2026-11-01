"""Auth page — login, register, and password reset flows."""


def build_login_page(*, providers: list[str], redirect_url: str | None = None) -> dict:
    return {
        "page_type": "login",
        "providers": [{"id": p, "label": p.title(), "icon": {"github": "🐙", "google": "🔵", "email": "📧"}.get(p, "🔑")}
                       for p in providers],
        "redirect_url": redirect_url,
        "features": ["sso", "remember_me", "password_reset"],
    }


def build_register_page(*, providers: list[str], plans: list[dict]) -> dict:
    return {
        "page_type": "register",
        "providers": [{"id": p, "label": f"Sign up with {p.title()}"} for p in providers],
        "plans": plans,
        "fields": ["display_name", "email", "password", "agree_terms"],
        "terms_url": "/terms", "privacy_url": "/privacy",
    }


def build_password_reset_page() -> dict:
    return {
        "page_type": "password_reset",
        "fields": ["email"],
        "message": "Enter your email to receive a password reset link.",
        "success_message": "Check your email for a reset link.",
    }
