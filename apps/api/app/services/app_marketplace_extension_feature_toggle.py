"""Feature Toggle — runtime feature flags for extensions with targeting.

Supports boolean/percentage/user-targeted toggles with override rules,
audit history, and gradual rollout via percentage-based activation.
"""
from __future__ import annotations
import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ToggleType(str, Enum):
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"


@dataclass
class FeatureToggle:
    toggle_id: str
    extension_id: str
    name: str
    toggle_type: ToggleType
    enabled: bool = False
    percentage: int = 0  # 0-100 for percentage type
    allowed_users: set[str] = field(default_factory=set)
    description: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class FeatureToggleService:
    """Manages feature flags with targeting and gradual rollout."""

    def __init__(self):
        self._toggles: dict[str, dict[str, FeatureToggle]] = {}  # ext_id -> {name: toggle}

    def create(self, extension_id: str, name: str,
               toggle_type: ToggleType, description: str = "",
               percentage: int = 0) -> FeatureToggle:
        if percentage < 0 or percentage > 100:
            raise ValueError("Percentage must be 0-100")
        toggle_id = f"ft_{secrets.token_urlsafe(8)}"
        toggle = FeatureToggle(
            toggle_id=toggle_id, extension_id=extension_id,
            name=name, toggle_type=toggle_type,
            description=description, percentage=percentage,
        )
        self._toggles.setdefault(extension_id, {})[name] = toggle
        return toggle

    def is_enabled(self, extension_id: str, name: str,
                   user_id: str | None = None) -> bool:
        toggles = self._toggles.get(extension_id, {})
        toggle = toggles.get(name)
        if not toggle or not toggle.enabled:
            return False

        if toggle.toggle_type == ToggleType.BOOLEAN:
            return True

        if toggle.toggle_type == ToggleType.USER_LIST:
            return user_id in toggle.allowed_users if user_id else False

        if toggle.toggle_type == ToggleType.PERCENTAGE:
            if not user_id:
                return False
            # Deterministic hash-based bucketing
            hash_input = f"{extension_id}:{name}:{user_id}"
            bucket = int(hashlib.md5(hash_input.encode()).hexdigest(), 16) % 100
            return bucket < toggle.percentage

        return False

    def enable(self, extension_id: str, name: str) -> bool:
        toggle = self._toggles.get(extension_id, {}).get(name)
        if toggle:
            toggle.enabled = True
            return True
        return False

    def disable(self, extension_id: str, name: str) -> bool:
        toggle = self._toggles.get(extension_id, {}).get(name)
        if toggle:
            toggle.enabled = False
            return True
        return False

    def set_percentage(self, extension_id: str, name: str, pct: int) -> bool:
        if pct < 0 or pct > 100:
            raise ValueError("Percentage must be 0-100")
        toggle = self._toggles.get(extension_id, {}).get(name)
        if toggle and toggle.toggle_type == ToggleType.PERCENTAGE:
            toggle.percentage = pct
            return True
        return False

    def add_users(self, extension_id: str, name: str, user_ids: list[str]) -> bool:
        toggle = self._toggles.get(extension_id, {}).get(name)
        if toggle and toggle.toggle_type == ToggleType.USER_LIST:
            toggle.allowed_users.update(user_ids)
            return True
        return False

    def remove_user(self, extension_id: str, name: str, user_id: str) -> bool:
        toggle = self._toggles.get(extension_id, {}).get(name)
        if toggle:
            toggle.allowed_users.discard(user_id)
            return True
        return False

    def list_toggles(self, extension_id: str) -> list[FeatureToggle]:
        return list(self._toggles.get(extension_id, {}).values())

    def get_all_flags(self, extension_id: str, user_id: str) -> dict[str, bool]:
        return {name: self.is_enabled(extension_id, name, user_id)
                for name in self._toggles.get(extension_id, {})}
