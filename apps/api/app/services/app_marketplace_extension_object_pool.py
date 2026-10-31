"""Object Pool — manage reusable expensive objects (connections, workers).

Implements:
- Fixed-size pool with borrow/return lifecycle
- Wait queue when pool exhausted
- Health check on borrow (validate before use)
- Idle eviction (remove stale objects)
- Pool growth/shrink with min/max bounds
- Metrics: active, idle, wait count, borrow latency
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import deque


@dataclass
class PooledObject:
    obj_id: str
    created_at: float
    last_used: float = 0.0
    borrow_count: int = 0
    healthy: bool = True
    in_use: bool = False


class ObjectPoolService:
    def __init__(self, min_size: int = 2, max_size: int = 10,
                 max_idle_seconds: float = 300,
                 factory: callable | None = None,
                 validator: callable | None = None):
        self._min_size = min_size
        self._max_size = max_size
        self._max_idle = max_idle_seconds
        self._factory = factory or (lambda i: f"obj-{i}")
        self._validator = validator or (lambda obj: True)
        self._pool: dict[str, PooledObject] = {}
        self._counter = 0
        self._total_borrows = 0
        self._total_wait_time = 0.0
        self._wait_queue: deque[float] = deque()  # timestamps of waiting requests

        # Pre-fill minimum
        for _ in range(min_size):
            self._create_object()

    def _create_object(self) -> PooledObject:
        self._counter += 1
        obj_id = str(self._factory(self._counter))
        po = PooledObject(obj_id=obj_id, created_at=time.time())
        self._pool[obj_id] = po
        return po

    def borrow(self) -> PooledObject | None:
        """Borrow an object from pool. Returns None if pool exhausted."""
        start = time.time()

        # Evict idle objects first
        self._evict_idle()

        # Find idle, healthy object
        for po in self._pool.values():
            if not po.in_use and po.healthy:
                if self._validator(po):
                    po.in_use = True
                    po.last_used = time.time()
                    po.borrow_count += 1
                    self._total_borrows += 1
                    self._total_wait_time += time.time() - start
                    return po
                else:
                    po.healthy = False  # failed validation

        # No idle objects — can we grow?
        if len(self._pool) < self._max_size:
            po = self._create_object()
            po.in_use = True
            po.last_used = time.time()
            po.borrow_count += 1
            self._total_borrows += 1
            return po

        # Pool exhausted
        self._wait_queue.append(time.time())
        return None

    def return_obj(self, obj_id: str, healthy: bool = True) -> bool:
        """Return an object to the pool."""
        po = self._pool.get(obj_id)
        if not po or not po.in_use:
            return False
        po.in_use = False
        po.last_used = time.time()
        po.healthy = healthy

        # If unhealthy and we have spares, destroy it
        if not healthy and len(self._pool) > self._min_size:
            del self._pool[obj_id]
            # Replace if below minimum
            if self._idle_count() < self._min_size:
                self._create_object()
        return True

    def _evict_idle(self) -> int:
        """Remove objects idle longer than max_idle_seconds."""
        now = time.time()
        to_evict = []
        for obj_id, po in self._pool.items():
            if not po.in_use and po.last_used > 0:
                if now - po.last_used > self._max_idle:
                    to_evict.append(obj_id)

        # Don't evict below minimum
        evictable = len(to_evict)
        keep = max(0, self._min_size - (len(self._pool) - evictable))
        to_evict = to_evict[:evictable - keep] if keep > 0 else to_evict

        for obj_id in to_evict:
            del self._pool[obj_id]
        return len(to_evict)

    def _idle_count(self) -> int:
        return sum(1 for po in self._pool.values() if not po.in_use and po.healthy)

    def stats(self) -> dict:
        active = sum(1 for po in self._pool.values() if po.in_use)
        idle = sum(1 for po in self._pool.values() if not po.in_use and po.healthy)
        unhealthy = sum(1 for po in self._pool.values() if not po.healthy)
        avg_wait = (self._total_wait_time / self._total_borrows * 1000) if self._total_borrows else 0
        return {
            "total_size": len(self._pool),
            "active": active,
            "idle": idle,
            "unhealthy": unhealthy,
            "min_size": self._min_size,
            "max_size": self._max_size,
            "total_borrows": self._total_borrows,
            "avg_wait_ms": round(avg_wait, 2),
            "pending_waiters": len(self._wait_queue),
        }
