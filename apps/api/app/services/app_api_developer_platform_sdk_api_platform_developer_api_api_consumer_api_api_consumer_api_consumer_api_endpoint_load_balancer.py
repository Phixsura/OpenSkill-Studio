"""Consumer API Endpoint Load Balancer — distribute requests across backend instances."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class BackendInstance:
    instance_id: str
    host: str
    port: int
    weight: int = 1
    healthy: bool = True
    active_connections: int = 0

@dataclass
class LBConfig:
    endpoint_path: str
    strategy: str = "round_robin"  # "round_robin", "least_connections", "weighted"
    health_check_interval_sec: int = 30

@dataclass
class RouteDecision:
    instance_id: str
    host: str
    port: int
    strategy_used: str

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancer:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], LBConfig] = {}
        self._instances: dict[tuple[str, str], list[BackendInstance]] = {}  # (inst, path) -> backends
        self._rr_index: dict[tuple[str, str], int] = {}

    def configure(self, installation_id: str, config: LBConfig) -> LBConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.strategy not in ("round_robin", "least_connections", "weighted"):
            raise ValueError(f"Invalid strategy: {config.strategy}")
        self._configs[(installation_id, config.endpoint_path)] = config
        return config

    def add_instance(self, installation_id: str, endpoint_path: str, instance: BackendInstance) -> BackendInstance:
        key = (installation_id, endpoint_path)
        if key not in self._instances:
            self._instances[key] = []
        self._instances[key].append(instance)
        return instance

    def remove_instance(self, installation_id: str, endpoint_path: str, instance_id: str) -> None:
        key = (installation_id, endpoint_path)
        instances = self._instances.get(key, [])
        self._instances[key] = [i for i in instances if i.instance_id != instance_id]

    def route(self, installation_id: str, endpoint_path: str) -> RouteDecision:
        key = (installation_id, endpoint_path)
        config = self._configs.get(key, LBConfig(endpoint_path=endpoint_path))
        instances = [i for i in self._instances.get(key, []) if i.healthy]
        if not instances:
            raise ValueError("No healthy instances available")
        if config.strategy == "round_robin":
            idx = self._rr_index.get(key, 0) % len(instances)
            self._rr_index[key] = idx + 1
            chosen = instances[idx]
        elif config.strategy == "least_connections":
            chosen = min(instances, key=lambda i: i.active_connections)
        else:  # weighted
            total_weight = sum(i.weight for i in instances)
            rr_idx = self._rr_index.get(key, 0) % total_weight
            self._rr_index[key] = rr_idx + 1
            cumulative = 0
            chosen = instances[-1]
            for inst in instances:
                cumulative += inst.weight
                if rr_idx < cumulative:
                    chosen = inst
                    break
        chosen.active_connections += 1
        return RouteDecision(instance_id=chosen.instance_id, host=chosen.host, port=chosen.port, strategy_used=config.strategy)

    def release(self, installation_id: str, endpoint_path: str, instance_id: str) -> None:
        for inst in self._instances.get((installation_id, endpoint_path), []):
            if inst.instance_id == instance_id:
                inst.active_connections = max(0, inst.active_connections - 1)
                break

    def list_instances(self, installation_id: str, endpoint_path: str) -> list[BackendInstance]:
        return self._instances.get((installation_id, endpoint_path), [])
