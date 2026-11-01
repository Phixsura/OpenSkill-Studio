"""Developer Settings — manage developer account preferences.

Stores notification preferences, API defaults, theme, timezone,
and extension publishing defaults.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DeveloperSettings:
    developer_id: str
    display_name: str = ""
    email_notifications: bool = True
    webhook_notifications: bool = False
    default_runtime: str = "node20"
    default_visibility: str = "public"
    theme: str = "system"
    timezone: str = "UTC"
    auto_deploy: bool = False
    two_factor_enabled: bool = False


class DeveloperSettingsService:
    """Manages developer account settings."""

    VALID_RUNTIMES = {"node18", "node20", "python3.11", "python3.12", "deno", "bun"}
    VALID_THEMES = {"light", "dark", "system"}

    def __init__(self):
        self._settings: dict[str, DeveloperSettings] = {}

    def get_or_create(self, developer_id: str) -> DeveloperSettings:
        if developer_id not in self._settings:
            self._settings[developer_id] = DeveloperSettings(developer_id=developer_id)
        return self._settings[developer_id]

    def update(self, developer_id: str, **kwargs) -> DeveloperSettings | dict:
        settings = self.get_or_create(developer_id)
        errors = []
        if "default_runtime" in kwargs and kwargs["default_runtime"] not in self.VALID_RUNTIMES:
            errors.append(f"Invalid runtime: {kwargs['default_runtime']}")
        if "theme" in kwargs and kwargs["theme"] not in self.VALID_THEMES:
            errors.append(f"Invalid theme: {kwargs['theme']}")
        if errors:
            return {"error": "Validation failed", "errors": errors}
        for key, val in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, val)
        return settings

    def get_settings(self, developer_id: str) -> dict:
        s = self.get_or_create(developer_id)
        return {k: v for k, v in s.__dict__.items()}

    def reset_defaults(self, developer_id: str) -> DeveloperSettings:
        self._settings[developer_id] = DeveloperSettings(developer_id=developer_id)
        return self._settings[developer_id]
