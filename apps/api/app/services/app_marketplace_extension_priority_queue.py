"""Priority Queue — binary heap with priority aging to prevent starvation.

Implements:
- Min-heap based priority queue (lower number = higher priority)
- Priority aging: waiting items gradually increase priority
- Priority levels: critical(0), high(1), normal(2), low(3)
- Peek without dequeue
- Batch dequeue
"""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import time


PRIORITY_LEVELS = {"critical": 0, "high": 1, "normal": 2, "low": 3}


@dataclass(order=True)
class PriorityItem:
    effective_priority: float = field(compare=True)
    enqueued_at: float = field(compare=True)
    sequence: int = field(compare=True)
    item_id: str = field(compare=False)
    payload: dict = field(compare=False, default_factory=dict)
    base_priority: int = field(compare=False, default=2)


class PriorityQueueService:
    def __init__(self, aging_rate: float = 0.1):
        """aging_rate: priority decrease per second of waiting (lower = higher priority)."""
        self._heap: list[PriorityItem] = []
        self._counter = 0
        self._aging_rate = aging_rate
        self._total_enqueued = 0
        self._total_dequeued = 0

    def enqueue(self, item_id: str, payload: dict,
                priority: str | int = "normal") -> PriorityItem:
        if isinstance(priority, str):
            priority_num = PRIORITY_LEVELS.get(priority, 2)
        else:
            priority_num = max(0, min(3, priority))

        self._counter += 1
        self._total_enqueued += 1
        item = PriorityItem(
            effective_priority=float(priority_num),
            enqueued_at=time.time(),
            sequence=self._counter,
            item_id=item_id,
            payload=payload,
            base_priority=priority_num)
        heapq.heappush(self._heap, item)
        return item

    def dequeue(self) -> PriorityItem | None:
        self._apply_aging()
        while self._heap:
            item = heapq.heappop(self._heap)
            self._total_dequeued += 1
            return item
        return None

    def dequeue_batch(self, count: int) -> list[PriorityItem]:
        self._apply_aging()
        items = []
        for _ in range(count):
            if not self._heap:
                break
            items.append(heapq.heappop(self._heap))
            self._total_dequeued += 1
        return items

    def peek(self) -> PriorityItem | None:
        self._apply_aging()
        return self._heap[0] if self._heap else None

    def _apply_aging(self) -> None:
        """Age all items: reduce effective_priority based on wait time."""
        if self._aging_rate <= 0:
            return
        now = time.time()
        new_heap = []
        for item in self._heap:
            wait_seconds = now - item.enqueued_at
            aged_priority = item.base_priority - (wait_seconds * self._aging_rate)
            aged_priority = max(0, aged_priority)  # can't go below 0
            item.effective_priority = aged_priority
            new_heap.append(item)
        heapq.heapify(new_heap)
        self._heap = new_heap

    def size(self) -> int:
        return len(self._heap)

    def stats(self) -> dict:
        by_priority = {name: 0 for name in PRIORITY_LEVELS}
        for item in self._heap:
            for name, level in PRIORITY_LEVELS.items():
                if item.base_priority == level:
                    by_priority[name] += 1
                    break
        return {
            "size": len(self._heap),
            "total_enqueued": self._total_enqueued,
            "total_dequeued": self._total_dequeued,
            "by_priority": by_priority,
        }
