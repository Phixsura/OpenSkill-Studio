"""API Feature Flag — manage feature flags for API behavior."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class FeatureFlag:
    flag_id: str
    name: str
    enabled: bool = False
    rollout_pct: int = 0  # 0-100
    allowlist: list[str] = field(default_factory=list)  # consumer_ids always included
    description: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlag:
    def __init__(self) -> None:
        self._flags: dict[tuple[str, str], FeatureFlag] = {}

    def create_flag(self, installation_id: str, flag: FeatureFlag) -> FeatureFlag:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= flag.rollout_pct <= 100: raise ValueError("rollout_pct must be 0-100")
        key = (installation_id, flag.flag_id)
        if key in self._flags: raise ValueError(f"Flag {flag.flag_id} already exists")
        self._flags[key] = flag
        return flag

    def is_enabled(self, installation_id: str, flag_id: str, consumer_id: str = "") -> bool:
        flag = self._flags.get((installation_id, flag_id))
        if flag is None: return False
        if not flag.enabled: return False
        if consumer_id in flag.allowlist: return True
        if flag.rollout_pct == 100: return True
        if flag.rollout_pct == 0: return False
        if consumer_id:
            h = int(hashlib.sha256(f"{flag_id}:{consumer_id}".encode()).hexdigest()[:8], 16)
            return (h % 100) < flag.rollout_pct
        return False

    def update_rollout(self, installation_id: str, flag_id: str, rollout_pct: int) -> FeatureFlag:
        flag = self._get(installation_id, flag_id)
        if not 0 <= rollout_pct <= 100: raise ValueError("rollout_pct must be 0-100")
        flag.rollout_pct = rollout_pct
        return flag

    def toggle(self, installation_id: str, flag_id: str, enabled: bool) -> FeatureFlag:
        flag = self._get(installation_id, flag_id)
        flag.enabled = enabled
        return flag

    def list_flags(self, installation_id: str) -> list[FeatureFlag]:
        return [f for (inst, _), f in self._flags.items() if inst == installation_id]

    def _get(self, installation_id: str, flag_id: str) -> FeatureFlag:
        f = self._flags.get((installation_id, flag_id))
        if f is None: raise KeyError(f"Flag {flag_id} not found")
        return f
