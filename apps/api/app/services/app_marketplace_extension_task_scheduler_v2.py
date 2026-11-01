"""Task Scheduler V2 — priority scheduling with deadlines and preemption.

Implements:
- Earliest Deadline First (EDF) scheduling
- Task preemption (higher priority interrupts lower)
- Dependency-aware scheduling (task waits for deps)
- Deadline miss detection
- Resource-constrained scheduling (CPU/memory limits)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import heapq


@dataclass
class ScheduledTask:
    task_id: str
    name: str
    priority: int = 0  # lower = higher priority
    deadline: float = 0  # unix timestamp, 0 = no deadline
    duration_ms: float = 100
    dependencies: list[str] = field(default_factory=list)
    cpu_required: float = 1.0  # cores
    memory_mb: float = 128
    status: str = "pending"  # pending, running, completed, preempted, missed
    started_at: float = 0.0
    completed_at: float = 0.0


class TaskSchedulerV2Service:
    def __init__(self, total_cpu: float = 4.0, total_memory_mb: float = 1024):
        self._tasks: dict[str, ScheduledTask] = {}
        self._total_cpu = total_cpu
        self._total_memory = total_memory_mb
        self._used_cpu = 0.0
        self._used_memory = 0.0
        self._completed: list[str] = []
        self._schedule_log: list[dict] = []

    def submit(self, task: ScheduledTask) -> None:
        self._tasks[task.task_id] = task

    def _get_ready_tasks(self) -> list[ScheduledTask]:
        """Tasks whose dependencies are all completed."""
        ready = []
        for task in self._tasks.values():
            if task.status != "pending":
                continue
            deps_met = all(d in self._completed for d in task.dependencies)
            if deps_met:
                ready.append(task)
        return ready

    def schedule(self) -> list[dict]:
        """Run one scheduling cycle. Returns actions taken."""
        now = time.time()
        actions = []

        # Check deadline misses
        for task in self._tasks.values():
            if task.status == "pending" and task.deadline > 0 and now > task.deadline:
                task.status = "missed"
                actions.append({"action": "deadline_missed", "task": task.task_id})

        ready = self._get_ready_tasks()
        if not ready:
            return actions

        # Sort by EDF (earliest deadline first), then priority
        def sort_key(t):
            dl = t.deadline if t.deadline > 0 else float('inf')
            return (dl, t.priority)
        ready.sort(key=sort_key)

        for task in ready:
            # Check resources
            if (self._used_cpu + task.cpu_required > self._total_cpu or
                    self._used_memory + task.memory_mb > self._total_memory):
                # Try preemption: find lower-priority running task
                preempted = self._try_preempt(task)
                if not preempted:
                    continue

            # Start task
            task.status = "running"
            task.started_at = now
            self._used_cpu += task.cpu_required
            self._used_memory += task.memory_mb
            actions.append({"action": "started", "task": task.task_id,
                            "priority": task.priority})

        self._schedule_log.extend(actions)
        return actions

    def _try_preempt(self, new_task: ScheduledTask) -> bool:
        """Preempt a lower-priority running task to make room."""
        running = [t for t in self._tasks.values() if t.status == "running"]
        # Find lowest priority (highest number) running task
        candidates = [t for t in running if t.priority > new_task.priority]
        if not candidates:
            return False

        victim = max(candidates, key=lambda t: t.priority)
        victim.status = "preempted"
        self._used_cpu -= victim.cpu_required
        self._used_memory -= victim.memory_mb
        # Re-queue preempted task
        victim.status = "pending"
        self._schedule_log.append({"action": "preempted", "task": victim.task_id,
                                    "by": new_task.task_id})
        return True

    def complete(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.status != "running":
            return False
        task.status = "completed"
        task.completed_at = time.time()
        self._used_cpu -= task.cpu_required
        self._used_memory -= task.memory_mb
        self._completed.append(task_id)
        return True

    def get_status(self) -> dict:
        by_status = {}
        for t in self._tasks.values():
            by_status[t.status] = by_status.get(t.status, 0) + 1
        return {
            "total_tasks": len(self._tasks),
            "by_status": by_status,
            "cpu_used": self._used_cpu,
            "cpu_total": self._total_cpu,
            "memory_used": self._used_memory,
            "memory_total": self._total_memory,
        }
