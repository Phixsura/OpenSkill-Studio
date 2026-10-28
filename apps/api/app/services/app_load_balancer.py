"""App Load Balancer — distribute requests across backend instances.

Manages load balancing for installed apps:
- Round-robin and weighted distribution
- Health-aware routing (skip unhealthy)
- Track request counts per instance
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
    """Distribute requests across backend instances."""

    def __init__(self) -> None:
        # installation_id → list[BackendInstance]
        self._pools: dict[str, list[BackendInstance]] = {}
        # installation_id → round-robin index
        self._rr_index: dict[str, int] = {}

    def add_instance(
        self,
        installation_id: str,
        instance_id: str,
        address: str,
        weight: int = 1,
    ) -> BackendInstance:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not instance_id:
            raise ValueError("instance_id is required")
        if not address:
            raise ValueError("address is required")
        if weight < 1:
            raise ValueError("weight must be >= 1")

        pool = self._pools.setdefault(installation_id, [])
        for inst in pool:
            if inst.instance_id == instance_id:
                raise ValueError(f"Instance {instance_id} already exists")

        instance = BackendInstance(
            instance_id=instance_id, address=address, weight=weight,
        )
        pool.append(instance)
        return instance

    def remove_instance(self, installation_id: str, instance_id: str) -> bool:
        pool = self._pools.get(installation_id, [])
        before = len(pool)
        self._pools[installation_id] = [i for i in pool if i.instance_id != instance_id]
        return len(self._pools[installation_id]) < before

    def next_instance(self, installation_id: str) -> BackendInstance:
        """Get the next healthy instance using weighted round-robin."""
        pool = self._pools.get(installation_id, [])
        healthy = [i for i in pool if i.healthy]
        if not healthy:
            raise ValueError("No healthy instances available")

        # Build weighted list
        weighted: list[BackendInstance] = []
        for inst in healthy:
            weighted.extend([inst] * inst.weight)

        idx = self._rr_index.get(installation_id, 0) % len(weighted)
        chosen = weighted[idx]
        self._rr_index[installation_id] = idx + 1
        chosen.request_count += 1
        return chosen

    def mark_unhealthy(self, installation_id: str, instance_id: str) -> None:
        inst = self._find(installation_id, instance_id)
        inst.healthy = False

    def mark_healthy(self, installation_id: str, instance_id: str) -> None:
        inst = self._find(installation_id, instance_id)
        inst.healthy = True

    def get_pool(self, installation_id: str) -> list[BackendInstance]:
        return list(self._pools.get(installation_id, []))

    def _find(self, installation_id: str, instance_id: str) -> BackendInstance:
        for inst in self._pools.get(installation_id, []):
            if inst.instance_id == instance_id:
                return inst
        raise KeyError(f"Instance {instance_id} not found")
