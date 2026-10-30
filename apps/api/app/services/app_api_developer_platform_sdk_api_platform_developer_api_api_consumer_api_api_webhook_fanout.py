"""API Consumer Webhook Fanout — fan out events to multiple consumer endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class FanoutTarget:
    target_id: str
    url: str
    active: bool = True
    delivery_count: int = 0
    failure_count: int = 0

@dataclass
class FanoutConfig:
    consumer_id: str
    targets: list[FanoutTarget] = field(default_factory=list)
    max_targets: int = 10

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookFanout:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], FanoutConfig] = {}

    def configure(self, installation_id: str, config: FanoutConfig) -> FanoutConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if len(config.targets) > config.max_targets:
            raise ValueError(f"Too many targets: {len(config.targets)} > {config.max_targets}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def add_target(self, installation_id: str, consumer_id: str, target: FanoutTarget) -> FanoutConfig:
        config = self._get(installation_id, consumer_id)
        if len(config.targets) >= config.max_targets:
            raise ValueError("Max targets reached")
        if any(t.target_id == target.target_id for t in config.targets):
            raise ValueError(f"Target {target.target_id} already exists")
        config.targets.append(target)
        return config

    def fanout(self, installation_id: str, consumer_id: str) -> list[FanoutTarget]:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: return []
        active = [t for t in config.targets if t.active]
        for t in active: t.delivery_count += 1
        return active

    def record_failure(self, installation_id: str, consumer_id: str, target_id: str) -> None:
        config = self._configs.get((installation_id, consumer_id))
        if config:
            for t in config.targets:
                if t.target_id == target_id: t.failure_count += 1; break

    def list_configs(self, installation_id: str) -> list[FanoutConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

    def _get(self, installation_id: str, consumer_id: str) -> FanoutConfig:
        c = self._configs.get((installation_id, consumer_id))
        if c is None: raise KeyError(f"No fanout config for {consumer_id}")
        return c
