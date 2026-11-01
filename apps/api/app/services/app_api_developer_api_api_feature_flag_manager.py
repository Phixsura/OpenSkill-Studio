"""App API Developer API Feature Flag Manager — manage API feature toggles."""
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
    description: str = ""
    evaluation_count: int = 0

class AppAPIDeveloperAPIApiFeatureFlagManager:
    def __init__(self) -> None:
        self._flags: dict[tuple[str, str], FeatureFlag] = {}

    def create(self, installation_id: str, flag_id: str, name: str, enabled: bool = False, rollout_pct: int = 0, description: str = "") -> FeatureFlag:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= rollout_pct <= 100: raise ValueError("rollout_pct must be 0-100")
        key = (installation_id, flag_id)
        if key in self._flags: raise ValueError(f"Flag {flag_id} exists")
        f = FeatureFlag(flag_id=flag_id, name=name, enabled=enabled, rollout_pct=rollout_pct, description=description)
        self._flags[key] = f
        return f

    def evaluate(self, installation_id: str, flag_id: str, consumer_id: str = "") -> bool:
        f = self._get(installation_id, flag_id)
        f.evaluation_count += 1
        if not f.enabled: return False
        if f.rollout_pct == 100: return True
        if f.rollout_pct == 0: return False
        h = int(hashlib.sha256(f"{flag_id}:{consumer_id}".encode()).hexdigest()[:8], 16)
        return (h % 100) < f.rollout_pct

    def toggle(self, installation_id: str, flag_id: str, enabled: bool) -> FeatureFlag:
        f = self._get(installation_id, flag_id)
        f.enabled = enabled
        return f

    def set_rollout(self, installation_id: str, flag_id: str, rollout_pct: int) -> FeatureFlag:
        if not 0 <= rollout_pct <= 100: raise ValueError("rollout_pct must be 0-100")
        f = self._get(installation_id, flag_id)
        f.rollout_pct = rollout_pct
        return f

    def list_flags(self, installation_id: str) -> list[FeatureFlag]:
        return [f for (inst, _), f in self._flags.items() if inst == installation_id]

    def _get(self, installation_id: str, flag_id: str) -> FeatureFlag:
        key = (installation_id, flag_id)
        f = self._flags.get(key)
        if f is None: raise KeyError(f"Flag {flag_id} not found")
        return f
