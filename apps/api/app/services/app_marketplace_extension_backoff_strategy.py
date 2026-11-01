"""Backoff Strategy — pluggable retry delay strategies with decorrelation.

Implements:
- Exponential backoff: base * 2^attempt
- Decorrelated jitter (AWS-style): rand(base, prev * 3)
- Equal jitter: (delay/2) + rand(0, delay/2)
- Full jitter: rand(0, delay)
- Linear backoff: base * attempt
- Fibonacci backoff: fib(attempt) * base
- Max delay cap for all strategies
"""
from __future__ import annotations
import random
import math


class BackoffStrategyService:
    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def exponential(self, attempt: int, base_ms: float = 100,
                    max_ms: float = 30000) -> float:
        """Simple exponential: base * 2^attempt."""
        delay = base_ms * (2 ** attempt)
        return min(delay, max_ms)

    def full_jitter(self, attempt: int, base_ms: float = 100,
                    max_ms: float = 30000) -> float:
        """Full jitter: rand(0, min(max, base * 2^attempt)).
        Best for reducing thundering herd."""
        ceiling = min(max_ms, base_ms * (2 ** attempt))
        return self._rng.uniform(0, ceiling)

    def equal_jitter(self, attempt: int, base_ms: float = 100,
                     max_ms: float = 30000) -> float:
        """Equal jitter: half deterministic + half random.
        Guarantees minimum delay while adding jitter."""
        ceiling = min(max_ms, base_ms * (2 ** attempt))
        half = ceiling / 2
        return half + self._rng.uniform(0, half)

    def decorrelated(self, prev_ms: float, base_ms: float = 100,
                     max_ms: float = 30000) -> float:
        """Decorrelated jitter (AWS-recommended):
        sleep = min(max, rand(base, prev * 3)).
        Each delay depends on the previous, not the attempt number."""
        delay = self._rng.uniform(base_ms, max(base_ms, prev_ms * 3))
        return min(delay, max_ms)

    def linear(self, attempt: int, base_ms: float = 100,
               max_ms: float = 30000) -> float:
        """Linear: base * (attempt + 1)."""
        delay = base_ms * (attempt + 1)
        return min(delay, max_ms)

    def fibonacci(self, attempt: int, base_ms: float = 100,
                  max_ms: float = 30000) -> float:
        """Fibonacci: fib(attempt) * base. Grows slower than exponential."""
        a, b = 1, 1
        for _ in range(attempt):
            a, b = b, a + b
        delay = a * base_ms
        return min(delay, max_ms)

    def compute_sequence(self, strategy: str, attempts: int,
                         base_ms: float = 100, max_ms: float = 30000) -> list[float]:
        """Generate a full sequence of delays for N attempts."""
        delays = []
        prev = base_ms
        for i in range(attempts):
            if strategy == "exponential":
                d = self.exponential(i, base_ms, max_ms)
            elif strategy == "full_jitter":
                d = self.full_jitter(i, base_ms, max_ms)
            elif strategy == "equal_jitter":
                d = self.equal_jitter(i, base_ms, max_ms)
            elif strategy == "decorrelated":
                d = self.decorrelated(prev, base_ms, max_ms)
                prev = d
            elif strategy == "linear":
                d = self.linear(i, base_ms, max_ms)
            elif strategy == "fibonacci":
                d = self.fibonacci(i, base_ms, max_ms)
            else:
                d = self.exponential(i, base_ms, max_ms)
            delays.append(round(d, 1))
        return delays

    def total_wait(self, strategy: str, attempts: int,
                   base_ms: float = 100, max_ms: float = 30000) -> float:
        """Total time spent waiting across all retry attempts."""
        return round(sum(self.compute_sequence(strategy, attempts, base_ms, max_ms)), 1)
