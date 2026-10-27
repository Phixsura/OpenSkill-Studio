"""Extension Feature Flag Service — dynamic feature flags per extension."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib


@dataclass
class FeatureFlag:
    flag_id: str
    name: str
    description: str = ""
    enabled: bool = False
    rollout_pct: int = 0  # 0-100
    allowlist: set[str] = field(default_factory=set)
    blocklist: set[str] = field(default_factory=set)


class ExtFeatureFlagSvcService:
    def __init__(self):
        self._flags: dict[str, dict[str, FeatureFlag]] = {}  # ext_id -> {flag_id -> flag}

    def create(self, extension_id: str, flag_id: str, name: str,
               description: str = "") -> FeatureFlag:
        flag = FeatureFlag(flag_id=flag_id, name=name, description=description)
        if extension_id not in self._flags:
            self._flags[extension_id] = {}
        self._flags[extension_id][flag_id] = flag
        return flag

    def set_enabled(self, extension_id: str, flag_id: str, enabled: bool) -> bool:
        flag = self._flags.get(extension_id, {}).get(flag_id)
        if not flag: return False
        flag.enabled = enabled
        return True

    def set_rollout(self, extension_id: str, flag_id: str, pct: int) -> bool:
        if pct < 0 or pct > 100: return False
        flag = self._flags.get(extension_id, {}).get(flag_id)
        if not flag: return False
        flag.rollout_pct = pct
        flag.enabled = True
        return True

    def is_enabled(self, extension_id: str, flag_id: str, user_id: str = "") -> bool:
        flag = self._flags.get(extension_id, {}).get(flag_id)
        if not flag or not flag.enabled: return False
        if user_id in flag.blocklist: return False
        if user_id in flag.allowlist: return True
        if flag.rollout_pct >= 100: return True
        if flag.rollout_pct <= 0: return bool(flag.allowlist)
        h = int(hashlib.md5(f"{flag_id}:{user_id}".encode()).hexdigest(), 16)
        return (h % 100) < flag.rollout_pct

    def get_all(self, extension_id: str) -> list[FeatureFlag]:
        return list(self._flags.get(extension_id, {}).values())

    def add_to_allowlist(self, extension_id: str, flag_id: str, user_id: str) -> bool:
        flag = self._flags.get(extension_id, {}).get(flag_id)
        if not flag: return False
        flag.allowlist.add(user_id)
        return True
