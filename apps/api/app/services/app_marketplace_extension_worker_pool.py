"""Worker Pool Scheduler — work-stealing with per-worker queues.

Implements:
- Fixed pool of workers with local queues
- Work stealing: idle workers steal from busy workers' queues
- Task affinity: prefer routing to same worker for cache locality
- Priority-aware scheduling
- Worker health monitoring
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import hashlib


@dataclass
class WorkerTask:
    task_id: str
    priority: int = 0  # lower = higher priority
    affinity_key: str = ""  # for routing to consistent worker
    payload: dict = field(default_factory=dict)
    assigned_to: str = ""
    status: str = "pending"


@dataclass
class Worker:
    worker_id: str
    queue: deque = field(default_factory=deque)
    processed: int = 0
    stolen_from: int = 0
    stolen_to: int = 0
    healthy: bool = True


class WorkerPoolService:
    def __init__(self, num_workers: int = 4):
        self._workers: list[Worker] = [
            Worker(worker_id=f"worker-{i}") for i in range(num_workers)
        ]
        self._total_submitted = 0
        self._total_steals = 0

    def submit(self, task_id: str, priority: int = 0,
               affinity_key: str = "", payload: dict | None = None) -> WorkerTask:
        """Submit task. Routes by affinity or least-loaded worker."""
        task = WorkerTask(task_id=task_id, priority=priority,
                          affinity_key=affinity_key, payload=payload or {})
        self._total_submitted += 1

        # Route by affinity if specified
        if affinity_key:
            worker = self._affinity_route(affinity_key)
        else:
            worker = self._least_loaded()

        task.assigned_to = worker.worker_id
        # Insert by priority (lower = higher priority, front of queue)
        if priority == 0:
            worker.queue.append(task)
        else:
            # Simple priority insertion
            inserted = False
            for i, existing in enumerate(worker.queue):
                if priority < existing.priority:
                    worker.queue.insert(i, task)
                    inserted = True
                    break
            if not inserted:
                worker.queue.append(task)

        return task

    def _affinity_route(self, key: str) -> Worker:
        """Consistent hash routing for cache locality."""
        healthy = [w for w in self._workers if w.healthy]
        if not healthy:
            return self._workers[0]
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return healthy[h % len(healthy)]

    def _least_loaded(self) -> Worker:
        healthy = [w for w in self._workers if w.healthy]
        if not healthy:
            return self._workers[0]
        return min(healthy, key=lambda w: len(w.queue))

    def process(self, worker_id: str) -> WorkerTask | None:
        """Worker processes next task from its queue."""
        worker = next((w for w in self._workers if w.worker_id == worker_id), None)
        if not worker or not worker.queue:
            # Try stealing from busiest worker
            return self._steal(worker) if worker else None

        task = worker.queue.popleft()
        task.status = "completed"
        worker.processed += 1
        return task

    def _steal(self, thief: Worker) -> WorkerTask | None:
        """Steal from the busiest worker's queue (take from back)."""
        candidates = sorted(
            [w for w in self._workers if w.healthy and w.worker_id != thief.worker_id],
            key=lambda w: len(w.queue), reverse=True)

        for victim in candidates:
            if len(victim.queue) >= 2:  # only steal if victim has enough
                task = victim.queue.pop()  # steal from back
                task.assigned_to = thief.worker_id
                task.status = "completed"
                thief.processed += 1
                thief.stolen_to += 1
                victim.stolen_from += 1
                self._total_steals += 1
                return task
        return None

    def process_all(self, max_per_worker: int = 10) -> int:
        """Process tasks across all workers."""
        total = 0
        for worker in self._workers:
            for _ in range(max_per_worker):
                task = self.process(worker.worker_id)
                if not task:
                    break
                total += 1
        return total

    def stats(self) -> dict:
        return {
            "workers": len(self._workers),
            "healthy": sum(1 for w in self._workers if w.healthy),
            "total_queued": sum(len(w.queue) for w in self._workers),
            "total_submitted": self._total_submitted,
            "total_processed": sum(w.processed for w in self._workers),
            "total_steals": self._total_steals,
            "per_worker": [{
                "id": w.worker_id, "queued": len(w.queue),
                "processed": w.processed, "stolen_from": w.stolen_from,
                "stolen_to": w.stolen_to
            } for w in self._workers],
        }
