"""Delayed Task Scheduler — heap-based scheduler with delay, retry, and cron-like repeating.

Implements:
- Schedule tasks with delay (fire after N seconds)
- Schedule at specific timestamp
- Repeating tasks with interval
- Retry failed tasks with backoff
- Cancel pending tasks
- Tick-based execution (poll for due tasks)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import time


@dataclass(order=True)
class ScheduledTask:
    fire_at: float
    sequence: int = field(compare=True)
    task_id: str = field(compare=False)
    handler: str = field(compare=False)
    payload: dict = field(compare=False, default_factory=dict)
    repeat_interval: float = field(compare=False, default=0)  # 0 = one-shot
    max_retries: int = field(compare=False, default=0)
    retry_count: int = field(compare=False, default=0)
    cancelled: bool = field(compare=False, default=False)


class DelayedSchedulerService:
    def __init__(self):
        self._heap: list[ScheduledTask] = []
        self._tasks: dict[str, ScheduledTask] = {}
        self._counter = 0
        self._executed: list[dict] = []

    def schedule_delay(self, handler: str, delay_seconds: float,
                       payload: dict | None = None, task_id: str = "",
                       repeat_interval: float = 0, max_retries: int = 0) -> ScheduledTask:
        """Schedule a task to fire after delay seconds."""
        return self._schedule(handler, time.time() + delay_seconds,
                              payload, task_id, repeat_interval, max_retries)

    def schedule_at(self, handler: str, fire_at: float,
                    payload: dict | None = None, task_id: str = "",
                    repeat_interval: float = 0, max_retries: int = 0) -> ScheduledTask:
        """Schedule a task at a specific timestamp."""
        return self._schedule(handler, fire_at, payload, task_id, repeat_interval, max_retries)

    def _schedule(self, handler: str, fire_at: float, payload: dict | None,
                  task_id: str, repeat_interval: float,
                  max_retries: int = 0) -> ScheduledTask:
        self._counter += 1
        if not task_id:
            task_id = f"task-{self._counter}"
        task = ScheduledTask(fire_at=fire_at, sequence=self._counter,
                             task_id=task_id, handler=handler,
                             payload=payload or {},
                             repeat_interval=repeat_interval,
                             max_retries=max_retries)
        heapq.heappush(self._heap, task)
        self._tasks[task_id] = task
        return task

    def cancel(self, task_id: str) -> bool:
        """Cancel a pending task (lazy deletion)."""
        task = self._tasks.get(task_id)
        if task and not task.cancelled:
            task.cancelled = True
            return True
        return False

    def tick(self, now: float | None = None, executor: callable | None = None) -> list[dict]:
        """Execute all tasks due at `now`. Returns list of executed task info."""
        now = now or time.time()
        executed = []

        while self._heap and self._heap[0].fire_at <= now:
            task = heapq.heappop(self._heap)
            if task.cancelled:
                continue

            # Execute
            result = {"task_id": task.task_id, "handler": task.handler,
                      "payload": task.payload, "fired_at": now}
            success = True
            if executor:
                try:
                    executor(task)
                except Exception as e:
                    success = False
                    result["error"] = str(e)

            if not success and task.retry_count < task.max_retries:
                # Retry with exponential backoff
                task.retry_count += 1
                backoff = 2 ** task.retry_count
                task.fire_at = now + backoff
                heapq.heappush(self._heap, task)
                result["retrying"] = True
                result["retry_at"] = task.fire_at
            elif task.repeat_interval > 0 and success:
                # Re-schedule repeating task
                task.fire_at = now + task.repeat_interval
                task.cancelled = False
                heapq.heappush(self._heap, task)
                result["next_fire"] = task.fire_at

            executed.append(result)
            self._executed.append(result)

        return executed

    def pending_count(self) -> int:
        return sum(1 for t in self._heap if not t.cancelled)

    def next_fire_time(self) -> float | None:
        while self._heap and self._heap[0].cancelled:
            heapq.heappop(self._heap)
        return self._heap[0].fire_at if self._heap else None

    def get_history(self, limit: int = 50) -> list[dict]:
        return self._executed[-limit:]
