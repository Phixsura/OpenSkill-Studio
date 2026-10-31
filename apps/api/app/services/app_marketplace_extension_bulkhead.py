"""Bulkhead Pattern — isolate failures by partitioning resources.

Ship hull analogy: compartmentalize so one leak doesn't sink the ship.

Implements:
- Named bulkheads with independent concurrency limits
- Semaphore-based admission control
- Queue with timeout for waiting requests
- Per-bulkhead metrics (active, queued, rejected)
- Adaptive sizing based on error rate
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import deque


@dataclass
class BulkheadConfig:
    name: str
    max_concurrent: int = 10
    max_queue: int = 20
    queue_timeout_ms: float = 5000


@dataclass
class BulkheadState:
    config: BulkheadConfig
    active: int = 0
    queued: int = 0
    total_accepted: int = 0
    total_rejected: int = 0
    total_timeout: int = 0
    total_errors: int = 0
    total_success: int = 0


@dataclass
class BulkheadToken:
    bulkhead: str
    token_id: str
    acquired_at: float = 0.0


class BulkheadService:
    def __init__(self):
        self._bulkheads: dict[str, BulkheadState] = {}
        self._counter = 0

    def create(self, config: BulkheadConfig) -> BulkheadState:
        state = BulkheadState(config=config)
        self._bulkheads[config.name] = state
        return state

    def try_acquire(self, name: str) -> BulkheadToken | None:
        """Try to acquire a slot in the bulkhead.
        Returns token if acquired, None if rejected."""
        state = self._bulkheads.get(name)
        if not state:
            return None

        if state.active < state.config.max_concurrent:
            state.active += 1
            state.total_accepted += 1
            self._counter += 1
            return BulkheadToken(bulkhead=name, token_id=f"bh-{self._counter}",
                                 acquired_at=time.time())

        # Check queue
        if state.queued < state.config.max_queue:
            state.queued += 1
            # Simulate waiting — in real impl this would block/async
            state.queued -= 1
            if state.active < state.config.max_concurrent:
                state.active += 1
                state.total_accepted += 1
                self._counter += 1
                return BulkheadToken(bulkhead=name, token_id=f"bh-{self._counter}",
                                     acquired_at=time.time())
            state.total_timeout += 1
            return None

        state.total_rejected += 1
        return None

    def release(self, token: BulkheadToken, success: bool = True) -> None:
        """Release a bulkhead slot."""
        state = self._bulkheads.get(token.bulkhead)
        if state and state.active > 0:
            state.active -= 1
            if success:
                state.total_success += 1
            else:
                state.total_errors += 1

    def get_state(self, name: str) -> dict | None:
        state = self._bulkheads.get(name)
        if not state:
            return None
        return {
            "name": name,
            "active": state.active,
            "max_concurrent": state.config.max_concurrent,
            "utilization": round(state.active / state.config.max_concurrent * 100, 1),
            "total_accepted": state.total_accepted,
            "total_rejected": state.total_rejected,
            "total_timeout": state.total_timeout,
            "error_rate": round(state.total_errors / max(1, state.total_success + state.total_errors) * 100, 1),
        }

    def get_all_states(self) -> dict[str, dict]:
        return {name: self.get_state(name) for name in self._bulkheads}

    def resize(self, name: str, max_concurrent: int) -> bool:
        """Dynamically resize a bulkhead."""
        state = self._bulkheads.get(name)
        if not state:
            return False
        state.config.max_concurrent = max(1, max_concurrent)
        return True

    def auto_resize(self, name: str, target_error_rate: float = 5.0) -> dict:
        """Adaptive sizing: shrink on high errors, grow on low errors."""
        state = self._bulkheads.get(name)
        if not state:
            return {}

        total = state.total_success + state.total_errors
        if total < 10:
            return {"action": "none", "reason": "insufficient data"}

        error_rate = state.total_errors / total * 100
        old_size = state.config.max_concurrent

        if error_rate > target_error_rate * 2:
            # High errors → reduce concurrency (shed load)
            new_size = max(1, old_size - max(1, old_size // 4))
            state.config.max_concurrent = new_size
            return {"action": "shrink", "from": old_size, "to": new_size,
                    "error_rate": round(error_rate, 1)}
        elif error_rate < target_error_rate / 2 and state.total_rejected > 0:
            # Low errors + rejections → grow
            new_size = old_size + max(1, old_size // 4)
            state.config.max_concurrent = new_size
            return {"action": "grow", "from": old_size, "to": new_size,
                    "error_rate": round(error_rate, 1)}

        return {"action": "none", "error_rate": round(error_rate, 1)}
