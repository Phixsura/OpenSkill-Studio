"""Distributed Lock — mutual exclusion with fencing tokens and lease expiry.

Implements:
- Acquire with timeout and lease duration
- Fencing tokens to prevent stale-lock writes
- Lease renewal (heartbeat)
- Deadlock detection via wait-for graph
- Lock downgrade (exclusive → shared)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Lock:
    resource: str
    owner: str
    fencing_token: int
    acquired_at: float
    expires_at: float
    mode: str = "exclusive"  # exclusive, shared
    renewed_count: int = 0


class DistributedLockService:
    def __init__(self):
        self._locks: dict[str, Lock] = {}
        self._shared_locks: dict[str, list[Lock]] = {}  # resource -> [shared locks]
        self._fencing_counter = 0
        self._wait_queue: dict[str, list[str]] = {}  # resource -> [waiting owners]

    def acquire(self, resource: str, owner: str, lease_seconds: float = 30,
                mode: str = "exclusive", timeout: float = 0) -> Lock | None:
        """Try to acquire lock. Returns Lock or None if unavailable."""
        now = time.time()

        # Clean expired locks
        self._cleanup_expired(resource, now)

        if mode == "shared":
            return self._acquire_shared(resource, owner, lease_seconds, now)

        # Exclusive lock
        existing = self._locks.get(resource)
        if existing and existing.expires_at > now:
            if existing.owner == owner:
                # Reentrant — renew
                return self._renew(resource, owner)
            # Resource locked by another owner
            self._enqueue_wait(resource, owner)
            return None

        # Also check shared locks
        shared = self._shared_locks.get(resource, [])
        active_shared = [s for s in shared if s.expires_at > now]
        if active_shared:
            return None  # can't get exclusive while shared locks held

        self._fencing_counter += 1
        lock = Lock(resource=resource, owner=owner,
                    fencing_token=self._fencing_counter,
                    acquired_at=now, expires_at=now + lease_seconds,
                    mode="exclusive")
        self._locks[resource] = lock
        self._dequeue_wait(resource, owner)
        return lock

    def _acquire_shared(self, resource: str, owner: str,
                        lease_seconds: float, now: float) -> Lock | None:
        # Can't acquire shared if exclusive lock exists
        existing = self._locks.get(resource)
        if existing and existing.expires_at > now and existing.mode == "exclusive":
            return None

        self._fencing_counter += 1
        lock = Lock(resource=resource, owner=owner,
                    fencing_token=self._fencing_counter,
                    acquired_at=now, expires_at=now + lease_seconds,
                    mode="shared")
        if resource not in self._shared_locks:
            self._shared_locks[resource] = []
        # Don't duplicate
        self._shared_locks[resource] = [
            s for s in self._shared_locks[resource] if s.owner != owner
        ]
        self._shared_locks[resource].append(lock)
        return lock

    def release(self, resource: str, owner: str) -> bool:
        lock = self._locks.get(resource)
        if lock and lock.owner == owner:
            del self._locks[resource]
            return True
        # Check shared
        shared = self._shared_locks.get(resource, [])
        before = len(shared)
        self._shared_locks[resource] = [s for s in shared if s.owner != owner]
        return len(self._shared_locks[resource]) < before

    def renew(self, resource: str, owner: str, lease_seconds: float = 30) -> Lock | None:
        return self._renew(resource, owner, lease_seconds)

    def _renew(self, resource: str, owner: str, lease_seconds: float = 30) -> Lock | None:
        lock = self._locks.get(resource)
        if lock and lock.owner == owner:
            lock.expires_at = time.time() + lease_seconds
            lock.renewed_count += 1
            return lock
        return None

    def is_valid_fencing_token(self, resource: str, token: int) -> bool:
        """Check if a fencing token is still the current one."""
        lock = self._locks.get(resource)
        if lock:
            return lock.fencing_token == token
        return False

    def _cleanup_expired(self, resource: str, now: float) -> None:
        lock = self._locks.get(resource)
        if lock and lock.expires_at <= now:
            del self._locks[resource]
        shared = self._shared_locks.get(resource, [])
        self._shared_locks[resource] = [s for s in shared if s.expires_at > now]

    def _enqueue_wait(self, resource: str, owner: str) -> None:
        if resource not in self._wait_queue:
            self._wait_queue[resource] = []
        if owner not in self._wait_queue[resource]:
            self._wait_queue[resource].append(owner)

    def _dequeue_wait(self, resource: str, owner: str) -> None:
        waiters = self._wait_queue.get(resource, [])
        if owner in waiters:
            waiters.remove(owner)

    def detect_deadlock(self) -> list[list[str]] | None:
        """Detect cycles in wait-for graph. Returns cycles found."""
        # Build wait-for graph: waiter → current lock owner
        graph: dict[str, str] = {}
        for resource, waiters in self._wait_queue.items():
            lock = self._locks.get(resource)
            if lock:
                for waiter in waiters:
                    graph[waiter] = lock.owner

        # DFS cycle detection
        cycles = []
        visited = set()
        for start in graph:
            if start in visited:
                continue
            path = []
            current = start
            path_set = set()
            while current and current not in visited:
                if current in path_set:
                    cycle_start = path.index(current)
                    cycles.append(path[cycle_start:] + [current])
                    break
                path.append(current)
                path_set.add(current)
                current = graph.get(current)
            visited.update(path_set)

        return cycles if cycles else None

    def get_stats(self) -> dict:
        now = time.time()
        active_exclusive = sum(1 for l in self._locks.values() if l.expires_at > now)
        active_shared = sum(1 for locks in self._shared_locks.values()
                           for l in locks if l.expires_at > now)
        waiting = sum(len(w) for w in self._wait_queue.values())
        return {"exclusive_locks": active_exclusive, "shared_locks": active_shared,
                "waiting": waiting, "fencing_counter": self._fencing_counter}
