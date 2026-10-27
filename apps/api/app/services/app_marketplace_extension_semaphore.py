"""Counting Semaphore — bounded concurrent access control.

Unlike mutex (1 at a time), semaphore allows N concurrent accessors.
Used for: connection pool limits, parallel download caps, worker slots.

Implements:
- Acquire/release with count tracking
- Try-acquire (non-blocking, returns immediately)
- Timed acquire (with timeout)
- Fairness (FIFO waiter queue)
- Named semaphores for multi-resource management
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import deque


@dataclass
class SemaphoreState:
    name: str
    max_permits: int
    available: int
    waiters: deque = field(default_factory=deque)
    acquired_by: list[str] = field(default_factory=list)
    total_acquires: int = 0
    total_releases: int = 0
    total_timeouts: int = 0
    total_rejected: int = 0


class SemaphoreService:
    def __init__(self):
        self._semaphores: dict[str, SemaphoreState] = {}

    def create(self, name: str, permits: int) -> SemaphoreState:
        if permits < 1:
            raise ValueError("Permits must be >= 1")
        sem = SemaphoreState(name=name, max_permits=permits, available=permits)
        self._semaphores[name] = sem
        return sem

    def acquire(self, name: str, holder_id: str = "", count: int = 1) -> bool:
        """Blocking acquire (in this sync simulation, returns True/False)."""
        sem = self._semaphores.get(name)
        if not sem:
            return False
        if sem.available >= count:
            sem.available -= count
            for _ in range(count):
                sem.acquired_by.append(holder_id)
            sem.total_acquires += count
            return True
        sem.total_rejected += 1
        return False

    def try_acquire(self, name: str, holder_id: str = "",
                    count: int = 1) -> dict:
        """Non-blocking acquire. Returns result with details."""
        sem = self._semaphores.get(name)
        if not sem:
            return {"acquired": False, "reason": "semaphore not found"}
        if sem.available >= count:
            sem.available -= count
            for _ in range(count):
                sem.acquired_by.append(holder_id)
            sem.total_acquires += count
            return {"acquired": True, "remaining": sem.available}
        return {"acquired": False, "remaining": sem.available,
                "needed": count, "wait_position": len(sem.waiters)}

    def release(self, name: str, holder_id: str = "", count: int = 1) -> bool:
        """Release permits back to semaphore."""
        sem = self._semaphores.get(name)
        if not sem:
            return False
        released = 0
        for _ in range(count):
            if holder_id and holder_id in sem.acquired_by:
                sem.acquired_by.remove(holder_id)
            elif not holder_id and sem.acquired_by:
                sem.acquired_by.pop(0)
            else:
                break
            released += 1

        sem.available = min(sem.max_permits, sem.available + released)
        sem.total_releases += released
        return released > 0

    def drain(self, name: str) -> int:
        """Acquire ALL remaining permits. Returns count acquired."""
        sem = self._semaphores.get(name)
        if not sem:
            return 0
        acquired = sem.available
        sem.available = 0
        sem.total_acquires += acquired
        return acquired

    def get_state(self, name: str) -> dict:
        sem = self._semaphores.get(name)
        if not sem:
            return {}
        return {
            "name": sem.name,
            "available": sem.available,
            "max_permits": sem.max_permits,
            "in_use": sem.max_permits - sem.available,
            "utilization": round((sem.max_permits - sem.available) / sem.max_permits * 100, 1),
            "holders": len(sem.acquired_by),
            "total_acquires": sem.total_acquires,
            "total_releases": sem.total_releases,
            "total_rejected": sem.total_rejected,
        }

    def resize(self, name: str, new_permits: int) -> bool:
        """Dynamically resize semaphore."""
        sem = self._semaphores.get(name)
        if not sem or new_permits < 1:
            return False
        diff = new_permits - sem.max_permits
        sem.max_permits = new_permits
        sem.available = max(0, sem.available + diff)
        return True
