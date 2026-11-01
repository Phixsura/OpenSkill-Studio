"""API Consumer Load Balancer — distribute requests across backend instances."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class BackendInstance:
    instance_id: str
    host: str
    weight: int = 1
    healthy: bool = True
    active_connections: int = 0

@dataclass
class LoadBalancerConfig:
    strategy: str = "round_robin"  # "round_robin", "least_connections", "ip_hash"
    instances: list[BackendInstance] = field(default_factory=list)

VALID_STRATEGIES = {"round_robin", "least_connections", "ip_hash", "weighted"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiLoadBalancer:
    def __init__(self) -> None:
        self._configs: dict[str, LoadBalancerConfig] = {}
        self._counters: dict[str, int] = {}

    def configure(self, installation_id: str, config: LoadBalancerConfig) -> LoadBalancerConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.strategy not in VALID_STRATEGIES: raise ValueError(f"Invalid strategy: {config.strategy}")
        if not config.instances: raise ValueError("At least one instance required")
        self._configs[installation_id] = config
        self._counters[installation_id] = 0
        return config

    def select(self, installation_id: str, consumer_id: str = "") -> BackendInstance | None:
        config = self._configs.get(installation_id)
        if config is None: return None
        healthy = [i for i in config.instances if i.healthy]
        if not healthy: return None
        if config.strategy == "round_robin":
            idx = self._counters.get(installation_id, 0) % len(healthy)
            self._counters[installation_id] = idx + 1
            return healthy[idx]
        elif config.strategy == "least_connections":
            return min(healthy, key=lambda i: i.active_connections)
        elif config.strategy == "ip_hash" and consumer_id:
            h = int(hashlib.sha256(consumer_id.encode()).hexdigest()[:8], 16)
            return healthy[h % len(healthy)]
        return healthy[0]

    def mark_unhealthy(self, installation_id: str, instance_id: str) -> None:
        config = self._configs.get(installation_id)
        if config:
            for i in config.instances:
                if i.instance_id == instance_id: i.healthy = False

    def healthy_count(self, installation_id: str) -> int:
        config = self._configs.get(installation_id)
        if config is None: return 0
        return sum(1 for i in config.instances if i.healthy)
