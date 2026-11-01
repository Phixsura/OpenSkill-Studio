"""API Consumer Request Canary — canary deployments for API endpoint changes."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class CanaryConfig:
    canary_id: str
    endpoint: str
    method: str
    canary_pct: int = 10  # 0-100
    canary_version: str = ""
    stable_version: str = ""
    active: bool = True
    canary_errors: int = 0
    stable_errors: int = 0
    canary_requests: int = 0
    stable_requests: int = 0

    @property
    def canary_error_rate(self) -> float:
        if self.canary_requests == 0: return 0.0
        return round((self.canary_errors / self.canary_requests) * 100, 1)

    @property
    def should_rollback(self) -> bool:
        return self.canary_error_rate > 10 and self.canary_requests >= 10

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCanary:
    def __init__(self) -> None:
        self._canaries: dict[tuple[str, str], CanaryConfig] = {}

    def create(self, installation_id: str, config: CanaryConfig) -> CanaryConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= config.canary_pct <= 100: raise ValueError("canary_pct must be 0-100")
        self._canaries[(installation_id, config.canary_id)] = config
        return config

    def route(self, installation_id: str, canary_id: str, consumer_id: str) -> str:
        config = self._canaries.get((installation_id, canary_id))
        if config is None or not config.active: return "stable"
        h = int(hashlib.sha256(consumer_id.encode()).hexdigest()[:8], 16)
        if (h % 100) < config.canary_pct:
            config.canary_requests += 1
            return "canary"
        config.stable_requests += 1
        return "stable"

    def record_error(self, installation_id: str, canary_id: str, version: str) -> CanaryConfig:
        config = self._canaries.get((installation_id, canary_id))
        if config is None: raise KeyError(f"Canary {canary_id} not found")
        if version == "canary": config.canary_errors += 1
        else: config.stable_errors += 1
        return config

    def promote(self, installation_id: str, canary_id: str) -> CanaryConfig:
        config = self._canaries.get((installation_id, canary_id))
        if config is None: raise KeyError(f"Canary {canary_id} not found")
        config.canary_pct = 100
        return config

    def list_canaries(self, installation_id: str) -> list[CanaryConfig]:
        return [c for (inst, _), c in self._canaries.items() if inst == installation_id]
