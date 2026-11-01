"""Rate Shaper — hybrid traffic shaping combining burst allowance with smooth output.

Token bucket allows bursts up to capacity; leaky bucket smooths output.
This hybrid: accept bursts into a buffer, drain at a constant rate.

Implements:
- Accept phase: token bucket for burst admission
- Drain phase: constant rate output (leaky bucket)
- Queue depth monitoring with backpressure
- Priority lanes (high priority bypasses queue)
- Adaptive drain rate based on downstream health
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import time


@dataclass
class ShaperRequest:
    request_id: str
    priority: str = "normal"  # high, normal, low
    enqueued_at: float = 0.0
    size: int = 1


class RateShaperService:
    def __init__(self, burst_capacity: int = 100, drain_rate: float = 10.0):
        """burst_capacity: max queued requests. drain_rate: requests/second output."""
        self._burst_capacity = burst_capacity
        self._base_drain_rate = drain_rate
        self._drain_rate = drain_rate
        self._queue: deque[ShaperRequest] = deque()
        self._high_priority: deque[ShaperRequest] = deque()
        self._last_drain = time.time()
        self._total_accepted = 0
        self._total_rejected = 0
        self._total_drained = 0
        self._total_shaped = 0

    def submit(self, request_id: str, priority: str = "normal",
               size: int = 1) -> dict:
        """Submit a request for shaping."""
        req = ShaperRequest(request_id=request_id, priority=priority,
                            enqueued_at=time.time(), size=size)

        if priority == "high":
            self._high_priority.append(req)
            self._total_accepted += 1
            return {"accepted": True, "queue": "priority",
                    "position": len(self._high_priority)}

        total_queued = len(self._queue) + len(self._high_priority)
        if total_queued >= self._burst_capacity:
            self._total_rejected += 1
            return {"accepted": False, "reason": "queue full",
                    "queue_depth": total_queued, "capacity": self._burst_capacity}

        self._queue.append(req)
        self._total_accepted += 1
        wait_estimate = total_queued / max(0.1, self._drain_rate)
        return {"accepted": True, "queue": "normal",
                "position": len(self._queue),
                "estimated_wait_ms": round(wait_estimate * 1000, 1)}

    def drain(self, max_count: int = 0) -> list[ShaperRequest]:
        """Drain requests at the configured rate. Returns released requests."""
        now = time.time()
        elapsed = now - self._last_drain
        to_drain = int(elapsed * self._drain_rate) if not max_count else max_count

        if to_drain <= 0:
            return []

        self._last_drain = now
        released = []

        # Priority first
        while self._high_priority and len(released) < to_drain:
            released.append(self._high_priority.popleft())

        # Then normal
        while self._queue and len(released) < to_drain:
            released.append(self._queue.popleft())

        self._total_drained += len(released)
        return released

    def adjust_rate(self, factor: float) -> float:
        """Adjust drain rate. factor=0.5 halves rate, factor=2.0 doubles."""
        self._drain_rate = max(0.1, min(self._base_drain_rate * 10,
                                         self._drain_rate * factor))
        return self._drain_rate

    def set_rate(self, rate: float) -> None:
        self._drain_rate = max(0.1, rate)

    def backpressure_status(self) -> str:
        depth = len(self._queue) + len(self._high_priority)
        pct = depth / max(1, self._burst_capacity) * 100
        if pct >= 90: return "critical"
        if pct >= 70: return "warning"
        return "ok"

    def stats(self) -> dict:
        depth = len(self._queue) + len(self._high_priority)
        return {
            "queue_depth": depth,
            "priority_queue": len(self._high_priority),
            "normal_queue": len(self._queue),
            "capacity": self._burst_capacity,
            "drain_rate": round(self._drain_rate, 2),
            "backpressure": self.backpressure_status(),
            "total_accepted": self._total_accepted,
            "total_rejected": self._total_rejected,
            "total_drained": self._total_drained,
            "utilization_pct": round(depth / max(1, self._burst_capacity) * 100, 1),
        }
