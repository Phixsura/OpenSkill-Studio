"""Service Discovery — dynamic endpoint registration for extension services.

Extensions can register their service endpoints, the platform discovers
available services, routes traffic, and handles health-based deregistration.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import time


@dataclass
class ServiceInstance:
    instance_id: str
    extension_id: str
    service_name: str
    endpoint: str
    version: str
    metadata: dict = field(default_factory=dict)
    registered_at: str = ""
    last_heartbeat: float = 0.0
    healthy: bool = True

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.now(timezone.utc).isoformat()
        if not self.last_heartbeat:
            self.last_heartbeat = time.monotonic()


class ServiceDiscovery:
    """Dynamic service registry with health-based deregistration."""

    def __init__(self, heartbeat_timeout: float = 60.0):
        self._instances: dict[str, ServiceInstance] = {}
        self._heartbeat_timeout = heartbeat_timeout

    def register(self, instance: ServiceInstance) -> ServiceInstance:
        """Register a service instance."""
        self._instances[instance.instance_id] = instance
        return instance

    def deregister(self, instance_id: str) -> bool:
        return self._instances.pop(instance_id, None) is not None

    def heartbeat(self, instance_id: str) -> bool:
        """Update heartbeat timestamp for an instance."""
        inst = self._instances.get(instance_id)
        if inst:
            inst.last_heartbeat = time.monotonic()
            inst.healthy = True
            return True
        return False

    def discover(self, service_name: str, extension_id: str | None = None,
                 healthy_only: bool = True) -> list[ServiceInstance]:
        """Discover service instances by name."""
        self._check_health()
        instances = [i for i in self._instances.values() if i.service_name == service_name]
        if extension_id:
            instances = [i for i in instances if i.extension_id == extension_id]
        if healthy_only:
            instances = [i for i in instances if i.healthy]
        return instances

    def get_instance(self, instance_id: str) -> ServiceInstance | None:
        return self._instances.get(instance_id)

    def list_services(self) -> list[dict]:
        """List all unique service names with instance counts."""
        services: dict[str, dict] = {}
        self._check_health()
        for inst in self._instances.values():
            key = inst.service_name
            if key not in services:
                services[key] = {"name": key, "total": 0, "healthy": 0}
            services[key]["total"] += 1
            if inst.healthy:
                services[key]["healthy"] += 1
        return sorted(services.values(), key=lambda s: s["name"])

    def _check_health(self) -> None:
        """Mark instances as unhealthy if heartbeat expired."""
        now = time.monotonic()
        for inst in self._instances.values():
            if now - inst.last_heartbeat > self._heartbeat_timeout:
                inst.healthy = False
