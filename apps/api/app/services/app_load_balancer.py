"""App Load Balancer — distribute traffic across backend instances.

Manages load balancing:
- Register backend instances with weights
- Round-robin and weighted selection
- Health-aware routing (skip unhealthy)
- Per-installation scoped pools
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class BackendInstance:
    """A backend instance in the pool."""

    instance_id: str
    address: str
    weight: int = 1
    healthy: bool = True
    request_count: int = 0


class AppLoadBalancer:
    """Distribute traffic across backend instances."""

    def __init__(self) -> None:
        self._pools: dict[str, list[BackendInstance]] = {}
        self._counters: dict[str, int] = {}

    def add_instance(
        self, installation_id: str, instance_id: str, address: str,
        weight: int = 1,
    ) -> BackendInstance:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not address:
            raise ValueError("address is required")
        if weight < 1:
            raise ValueError("weight must be at least 1")

        pool = self._pools.setdefault(installation_id, [])
        # No duplicate instance_id
        if any(i.instance_id == instance_id for i in pool):
            raise ValueError(f"Instance {instance_id} already exists")

        inst = BackendInstance(instance_id=instance_id, address=address, weight=weight)
        pool.append(inst)
        return inst

    def next_instance(self, installation_id: str) -> BackendInstance:
        """Weighted round-robin selection, skipping unhealthy."""
        pool = self._pools.get(installation_id, [])
        healthy = [i for i in pool if i.healthy]
        if not healthy:
            raise ValueError("No healthy instances")

        # Build weighted list
        weighted: list[BackendInstance] = []
        for inst in healthy:
            weighted.extend([inst] * inst.weight)

        counter = self._counters.get(installation_id, 0)
        selected = weighted[counter % len(weighted)]
        self._counters[installation_id] = counter + 1
        selected.request_count += 1
        return selected

    def set_health(self, installation_id: str, instance_id: str, healthy: bool) -> BackendInstance:
        inst = self._find(installation_id, instance_id)
        inst.healthy = healthy
        return inst

    def remove_instance(self, installation_id: str, instance_id: str) -> bool:
        pool = self._pools.get(installation_id, [])
        for i, inst in enumerate(pool):
            if inst.instance_id == instance_id:
                pool.pop(i)
                return True
        return False

    def list_instances(self, installation_id: str) -> list[BackendInstance]:
        return list(self._pools.get(installation_id, []))

    def healthy_count(self, installation_id: str) -> int:
        return sum(1 for i in self._pools.get(installation_id, []) if i.healthy)

    def _find(self, installation_id: str, instance_id: str) -> BackendInstance:
        for inst in self._pools.get(installation_id, []):
            if inst.instance_id == instance_id:
                return inst
        raise KeyError(f"Instance {instance_id} not found")
