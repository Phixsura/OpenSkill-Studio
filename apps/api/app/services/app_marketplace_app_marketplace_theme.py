"""Marketplace theme — theming system for marketplace customization."""

THEMES = {
    "light": {"bg": "#ffffff", "text": "#1a1a1a", "primary": "#2563eb", "secondary": "#7c3aed", "border": "#e5e7eb"},
    "dark": {"bg": "#111827", "text": "#f9fafb", "primary": "#3b82f6", "secondary": "#8b5cf6", "border": "#374151"},
    "high_contrast": {"bg": "#000000", "text": "#ffffff", "primary": "#ffff00", "secondary": "#00ff00", "border": "#ffffff"},
}


def get_theme(*, theme_id: str) -> dict:
    return THEMES.get(theme_id, THEMES["light"])


def get_css_variables(*, theme_id: str) -> dict:
    theme = get_theme(theme_id=theme_id)
    return {f"--color-{k}": v for k, v in theme.items()}


def detect_preferred_theme(*, system_preference: str | None, user_preference: str | None) -> str:
    if user_preference and user_preference in THEMES:
        return user_preference
    if system_preference == "dark":
        return "dark"
    return "light"


def list_themes() -> list[dict]:
    return [{"id": k, "name": k.replace("_", " ").title(), "preview": v} for k, v in THEMES.items()]
