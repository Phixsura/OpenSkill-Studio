"""Feature Flags — toggle features for extensions per org/user/percentage.

Allows extensions to gate features behind flags that can be toggled
per organization, user, or rolled out to a percentage of users.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field


@dataclass
class FeatureFlag:
    flag_id: str
    extension_id: str
    name: str
    description: str = ""
    enabled_globally: bool = False
    rollout_percentage: int = 0  # 0-100
    enabled_orgs: set[str] = field(default_factory=set)
    enabled_users: set[str] = field(default_factory=set)
    disabled_orgs: set[str] = field(default_factory=set)


class FeatureFlagService:
    """Manages feature flags for extensions."""

    def __init__(self):
        self._flags: dict[str, FeatureFlag] = {}

    def create_flag(self, flag_id: str, extension_id: str, name: str,
                    description: str = "") -> FeatureFlag:
        flag = FeatureFlag(flag_id=flag_id, extension_id=extension_id,
                           name=name, description=description)
        self._flags[flag_id] = flag
        return flag

    def get_flag(self, flag_id: str) -> FeatureFlag | None:
        return self._flags.get(flag_id)

    def is_enabled(self, flag_id: str, org_id: str = "", user_id: str = "") -> bool:
        """Check if flag is enabled for given context."""
        flag = self._flags.get(flag_id)
        if not flag:
            return False

        # Explicit org disable overrides everything
        if org_id and org_id in flag.disabled_orgs:
            return False

        # Global toggle
        if flag.enabled_globally:
            return True

        # Explicit org enable
        if org_id and org_id in flag.enabled_orgs:
            return True

        # Explicit user enable
        if user_id and user_id in flag.enabled_users:
            return True

        # Percentage rollout based on stable hash
        if flag.rollout_percentage > 0 and user_id:
            hash_input = f"{flag_id}:{user_id}"
            hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            bucket = hash_val % 100
            return bucket < flag.rollout_percentage

        return False

    def enable_globally(self, flag_id: str) -> bool:
        flag = self._flags.get(flag_id)
        if flag:
            flag.enabled_globally = True
            return True
        return False

    def disable_globally(self, flag_id: str) -> bool:
        flag = self._flags.get(flag_id)
        if flag:
            flag.enabled_globally = False
            return True
        return False

    def set_rollout(self, flag_id: str, percentage: int) -> bool:
        flag = self._flags.get(flag_id)
        if flag and 0 <= percentage <= 100:
            flag.rollout_percentage = percentage
            return True
        return False

    def enable_for_org(self, flag_id: str, org_id: str) -> bool:
        flag = self._flags.get(flag_id)
        if flag:
            flag.enabled_orgs.add(org_id)
            flag.disabled_orgs.discard(org_id)
            return True
        return False

    def disable_for_org(self, flag_id: str, org_id: str) -> bool:
        flag = self._flags.get(flag_id)
        if flag:
            flag.disabled_orgs.add(org_id)
            flag.enabled_orgs.discard(org_id)
            return True
        return False

    def list_flags(self, extension_id: str | None = None) -> list[FeatureFlag]:
        flags = list(self._flags.values())
        if extension_id:
            flags = [f for f in flags if f.extension_id == extension_id]
        return flags
