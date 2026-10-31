"""API Consumer Endpoint Throttle Config — per-endpoint throttle configurations."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ThrottleConfig:
    endpoint: str
    method: str
    max_rps: int
    burst_size: int = 0
    throttle_action: str = "reject"  # "reject", "queue", "delay"
    total_throttled: int = 0
    total_served: int = 0

    @property
    def throttle_rate(self) -> float:
        total = self.total_throttled + self.total_served
        if total == 0: return 0.0
        return round((self.total_throttled / total) * 100, 1)

VALID_ACTIONS = {"reject", "queue", "delay"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointThrottleConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], ThrottleConfig] = {}

    def configure(self, installation_id: str, config: ThrottleConfig) -> ThrottleConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.max_rps < 1: raise ValueError("max_rps must be >= 1")
        if config.throttle_action not in VALID_ACTIONS: raise ValueError(f"Invalid action: {config.throttle_action}")
        self._configs[(installation_id, config.method.upper(), config.endpoint)] = config
        return config

    def check(self, installation_id: str, method: str, endpoint: str, current_rps: float) -> dict[str, object]:
        config = self._configs.get((installation_id, method.upper(), endpoint))
        if config is None: return {"throttled": False, "reason": "no_config"}
        if current_rps > config.max_rps + config.burst_size:
            config.total_throttled += 1
            return {"throttled": True, "action": config.throttle_action, "limit": config.max_rps}
        config.total_served += 1
        return {"throttled": False, "remaining_rps": config.max_rps - current_rps}

    def most_throttled(self, installation_id: str, limit: int = 5) -> list[ThrottleConfig]:
        configs = [c for (inst, _, _), c in self._configs.items() if inst == installation_id]
        return sorted(configs, key=lambda c: -c.total_throttled)[:limit]

    def list_configs(self, installation_id: str) -> list[ThrottleConfig]:
        return [c for (inst, _, _), c in self._configs.items() if inst == installation_id]
