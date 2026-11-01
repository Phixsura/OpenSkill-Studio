"""Consumer API Settings — unified consumer settings management."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class Setting:
    key: str
    value: str
    category: str = "general"  # "general", "security", "notifications", "billing", "api"
    description: str = ""
    is_secret: bool = False

VALID_CATEGORIES = {"general", "security", "notifications", "billing", "api", "display", "integrations"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings:
    def __init__(self) -> None:
        self._settings: dict[tuple[str, str, str], Setting] = {}  # (inst, consumer, key)

    def set(self, installation_id: str, consumer_id: str, setting: Setting) -> Setting:
        if not installation_id:
            raise ValueError("installation_id is required")
        if setting.category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {setting.category}")
        if not setting.key:
            raise ValueError("key is required")
        self._settings[(installation_id, consumer_id, setting.key)] = setting
        return setting

    def get(self, installation_id: str, consumer_id: str, key: str) -> Setting | None:
        setting = self._settings.get((installation_id, consumer_id, key))
        if setting and setting.is_secret:
            return Setting(key=setting.key, value="***", category=setting.category, description=setting.description, is_secret=True)
        return setting

    def get_raw(self, installation_id: str, consumer_id: str, key: str) -> str | None:
        """Internal use only — returns unmasked value."""
        setting = self._settings.get((installation_id, consumer_id, key))
        return setting.value if setting else None

    def delete(self, installation_id: str, consumer_id: str, key: str) -> None:
        k = (installation_id, consumer_id, key)
        if k not in self._settings:
            raise ValueError("Setting not found")
        del self._settings[k]

    def list_by_category(self, installation_id: str, consumer_id: str, category: str | None = None) -> list[Setting]:
        settings = [s for (inst, cid, _), s in self._settings.items() if inst == installation_id and cid == consumer_id]
        if category:
            settings = [s for s in settings if s.category == category]
        # Mask secrets
        result = []
        for s in sorted(settings, key=lambda s: (s.category, s.key)):
            if s.is_secret:
                result.append(Setting(key=s.key, value="***", category=s.category, description=s.description, is_secret=True))
            else:
                result.append(s)
        return result

    def get_categories(self, installation_id: str, consumer_id: str) -> list[str]:
        cats = {s.category for (inst, cid, _), s in self._settings.items() if inst == installation_id and cid == consumer_id}
        return sorted(cats)
