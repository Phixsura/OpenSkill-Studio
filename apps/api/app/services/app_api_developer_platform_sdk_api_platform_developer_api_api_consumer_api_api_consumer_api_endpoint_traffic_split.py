"""Endpoint Traffic Split — route traffic between endpoint versions by weight."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class TrafficTarget:
    target_id: str
    version: str
    weight: int  # 0-100

@dataclass
class SplitConfig:
    endpoint_path: str
    targets: list[TrafficTarget] = field(default_factory=list)
    sticky: bool = True  # same consumer always gets same target

    def validate(self) -> None:
        total = sum(t.weight for t in self.targets)
        if total != 100:
            raise ValueError(f"Weights must sum to 100, got {total}")
        if any(t.weight < 0 for t in self.targets):
            raise ValueError("Weights must be non-negative")

@dataclass
class RouteDecision:
    target_id: str
    version: str
    reason: str  # "sticky_hash" or "weight_random"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointTrafficSplit:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], SplitConfig] = {}

    def set_split(self, installation_id: str, config: SplitConfig) -> SplitConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        config.validate()
        self._configs[(installation_id, config.endpoint_path)] = config
        log.info("traffic_split_set", installation_id=installation_id, path=config.endpoint_path, targets=len(config.targets))
        return config

    def get_split(self, installation_id: str, endpoint_path: str) -> SplitConfig | None:
        return self._configs.get((installation_id, endpoint_path))

    def route(self, installation_id: str, endpoint_path: str, consumer_id: str) -> RouteDecision:
        config = self._configs.get((installation_id, endpoint_path))
        if not config or not config.targets:
            raise ValueError("No split configured")
        if config.sticky:
            h = int(hashlib.sha256(f"{installation_id}:{consumer_id}:{endpoint_path}".encode()).hexdigest(), 16)
            bucket = h % 100
        else:
            import random
            bucket = random.randint(0, 99)
        cumulative = 0
        for target in config.targets:
            cumulative += target.weight
            if bucket < cumulative:
                return RouteDecision(target_id=target.target_id, version=target.version, reason="sticky_hash" if config.sticky else "weight_random")
        last = config.targets[-1]
        return RouteDecision(target_id=last.target_id, version=last.version, reason="fallback")

    def list_splits(self, installation_id: str) -> list[SplitConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
