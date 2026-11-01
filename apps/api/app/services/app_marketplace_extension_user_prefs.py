"""Extension User Preferences — per-user marketplace preferences."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class UserPreferences:
    user_id: str
    theme: str = "system"  # light, dark, system
    language: str = "en"
    notifications_enabled: bool = True
    email_digest: str = "weekly"  # none, daily, weekly
    default_view: str = "grid"  # grid, list
    show_beta: bool = False
    auto_update: bool = True
    timezone: str = "UTC"


class ExtUserPrefsService:
    VALID_THEMES = {"light", "dark", "system"}
    VALID_DIGESTS = {"none", "daily", "weekly"}
    VALID_VIEWS = {"grid", "list"}

    def __init__(self):
        self._prefs: dict[str, UserPreferences] = {}

    def get(self, user_id: str) -> UserPreferences:
        if user_id not in self._prefs:
            self._prefs[user_id] = UserPreferences(user_id=user_id)
        return self._prefs[user_id]

    def update(self, user_id: str, **kwargs) -> tuple[bool, list[str]]:
        prefs = self.get(user_id)
        errors = []
        if "theme" in kwargs and kwargs["theme"] not in self.VALID_THEMES:
            errors.append(f"Invalid theme: {kwargs['theme']}")
        if "email_digest" in kwargs and kwargs["email_digest"] not in self.VALID_DIGESTS:
            errors.append(f"Invalid digest: {kwargs['email_digest']}")
        if "default_view" in kwargs and kwargs["default_view"] not in self.VALID_VIEWS:
            errors.append(f"Invalid view: {kwargs['default_view']}")
        if errors:
            return False, errors
        for k, v in kwargs.items():
            if hasattr(prefs, k):
                setattr(prefs, k, v)
        return True, []

    def reset(self, user_id: str) -> UserPreferences:
        self._prefs[user_id] = UserPreferences(user_id=user_id)
        return self._prefs[user_id]

    def export_prefs(self, user_id: str) -> dict:
        p = self.get(user_id)
        return {k: v for k, v in p.__dict__.items() if k != "user_id"}
