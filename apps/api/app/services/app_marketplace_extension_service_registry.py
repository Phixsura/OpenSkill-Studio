"""Service Registry — service discovery with heartbeat and health-aware routing.

Consul/Eureka-style service registry for microservices.

Implements:
- Service registration with metadata and tags
- Heartbeat-based liveness (TTL expiry)
- Health-aware routing (skip unhealthy instances)
- Tag-based service filtering
- Load-aware instance selection
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import hashlib


@dataclass
class ServiceInstance:
    instance_id: str
    service_name: str
    host: str
    port: int
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    healthy: bool = True
    last_heartbeat: float = 0.0
    registered_at: float = 0.0
    load: float = 0.0  # 0-1 reported load

    def __post_init__(self):
        now = time.time()
        if not self.registered_at: self.registered_at = now
        if not self.last_heartbeat: self.last_heartbeat = now

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


class ServiceRegistryService:
    HEARTBEAT_TTL = 30  # seconds before marking unhealthy

    def __init__(self):
        self._instances: dict[str, ServiceInstance] = {}  # instance_id -> instance
        self._services: dict[str, list[str]] = {}  # service_name -> [instance_ids]

    def register(self, service_name: str, host: str, port: int,
                 instance_id: str = "", tags: list[str] | None = None,
                 metadata: dict | None = None) -> ServiceInstance:
        if not instance_id:
            instance_id = hashlib.md5(f"{service_name}:{host}:{port}".encode()).hexdigest()[:12]

        instance = ServiceInstance(
            instance_id=instance_id, service_name=service_name,
            host=host, port=port, tags=tags or [],
            metadata=metadata or {})
        self._instances[instance_id] = instance

        if service_name not in self._services:
            self._services[service_name] = []
        if instance_id not in self._services[service_name]:
            self._services[service_name].append(instance_id)

        return instance

    def deregister(self, instance_id: str) -> bool:
        inst = self._instances.pop(instance_id, None)
        if inst:
            ids = self._services.get(inst.service_name, [])
            if instance_id in ids:
                ids.remove(instance_id)
            return True
        return False

    def heartbeat(self, instance_id: str, load: float = 0.0) -> bool:
        inst = self._instances.get(instance_id)
        if not inst:
            return False
        inst.last_heartbeat = time.time()
        inst.healthy = True
        inst.load = max(0, min(1, load))
        return True

    def check_health(self) -> int:
        """Mark instances as unhealthy if heartbeat expired. Returns count."""
        now = time.time()
        marked = 0
        for inst in self._instances.values():
            if inst.healthy and (now - inst.last_heartbeat) > self.HEARTBEAT_TTL:
                inst.healthy = False
                marked += 1
        return marked

    def discover(self, service_name: str, healthy_only: bool = True,
                 tags: list[str] | None = None) -> list[ServiceInstance]:
        """Find instances of a service."""
        ids = self._services.get(service_name, [])
        instances = [self._instances[iid] for iid in ids if iid in self._instances]

        if healthy_only:
            instances = [i for i in instances if i.healthy]
        if tags:
            instances = [i for i in instances if all(t in i.tags for t in tags)]

        return instances

    def resolve(self, service_name: str, strategy: str = "least_load",
                tags: list[str] | None = None) -> ServiceInstance | None:
        """Resolve one instance using a selection strategy."""
        instances = self.discover(service_name, healthy_only=True, tags=tags)
        if not instances:
            return None

        if strategy == "least_load":
            return min(instances, key=lambda i: i.load)
        elif strategy == "round_robin":
            # Simple: pick based on time hash
            idx = int(time.time() * 1000) % len(instances)
            return instances[idx]
        elif strategy == "random":
            import random
            return random.choice(instances)

        return instances[0]

    def get_all_services(self) -> dict[str, int]:
        result = {}
        for name, ids in self._services.items():
            healthy = sum(1 for iid in ids
                          if iid in self._instances and self._instances[iid].healthy)
            result[name] = healthy
        return result
