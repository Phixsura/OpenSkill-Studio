"""Consumer API Feature Flag — toggle features per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class FeatureFlag:
    flag_id: str
    name: str
    description: str = ""
    default_enabled: bool = False
    rollout_pct: int = 0  # 0-100

@dataclass
class ConsumerOverride:
    consumer_id: str
    flag_id: str
    enabled: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlag:
    def __init__(self) -> None:
        self._flags: dict[tuple[str, str], FeatureFlag] = {}
        self._overrides: dict[tuple[str, str, str], ConsumerOverride] = {}  # (inst, consumer, flag)

    def create_flag(self, installation_id: str, flag: FeatureFlag) -> FeatureFlag:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (0 <= flag.rollout_pct <= 100):
            raise ValueError("rollout_pct must be 0-100")
        key = (installation_id, flag.flag_id)
        if key in self._flags:
            raise ValueError(f"Flag {flag.flag_id} already exists")
        self._flags[key] = flag
        return flag

    def set_override(self, installation_id: str, override: ConsumerOverride) -> ConsumerOverride:
        if (installation_id, override.flag_id) not in self._flags:
            raise ValueError(f"Flag {override.flag_id} not found")
        self._overrides[(installation_id, override.consumer_id, override.flag_id)] = override
        return override

    def is_enabled(self, installation_id: str, consumer_id: str, flag_id: str) -> bool:
        # Check override first
        override = self._overrides.get((installation_id, consumer_id, flag_id))
        if override is not None:
            return override.enabled
        # Check flag default + rollout
        flag = self._flags.get((installation_id, flag_id))
        if not flag:
            return False
        if flag.default_enabled:
            return True
        if flag.rollout_pct > 0:
            # Deterministic hash-based rollout
            h = hash(f"{installation_id}:{consumer_id}:{flag_id}") % 100
            return h < flag.rollout_pct
        return False

    def list_flags(self, installation_id: str) -> list[FeatureFlag]:
        return sorted([f for (inst, _), f in self._flags.items() if inst == installation_id], key=lambda f: f.name)

    def get_consumer_flags(self, installation_id: str, consumer_id: str) -> dict[str, bool]:
        flags = [f for (inst, _), f in self._flags.items() if inst == installation_id]
        return {f.flag_id: self.is_enabled(installation_id, consumer_id, f.flag_id) for f in flags}
