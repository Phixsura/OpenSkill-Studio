"""Sampling Strategy — configurable sampling for high-volume data streams.

Implements:
- Fixed rate sampling (1 in N)
- Probabilistic sampling (p% of events)
- Reservoir sampling (fixed-size random sample from stream)
- Priority sampling (always keep high-value events)
- Adaptive sampling (adjust rate based on volume)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import random
import hashlib


@dataclass
class SampledEvent:
    event_id: str
    data: dict
    sampled: bool
    sample_rate: float  # what rate was used (for weight calculation)
    priority: str = "normal"


class SamplingStrategyService:
    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)
        self._reservoir: list[dict] = []
        self._reservoir_size = 100
        self._stream_count = 0
        self._adaptive_count = 0
        self._adaptive_window_start = 0.0

    def fixed_rate(self, event_id: str, data: dict,
                   rate: int = 10) -> SampledEvent:
        """Keep 1 in every N events. Deterministic via hash."""
        h = int(hashlib.md5(event_id.encode()).hexdigest()[:8], 16)
        sampled = (h % rate) == 0
        return SampledEvent(event_id, data, sampled, 1.0 / rate)

    def probabilistic(self, event_id: str, data: dict,
                      probability: float = 0.1) -> SampledEvent:
        """Keep each event with probability p."""
        h = int(hashlib.md5(event_id.encode()).hexdigest()[:8], 16)
        sampled = (h % 10000) < int(probability * 10000)
        return SampledEvent(event_id, data, sampled, probability)

    def priority_sample(self, event_id: str, data: dict,
                        priority: str = "normal",
                        base_rate: float = 0.1) -> SampledEvent:
        """Always keep high-priority events, sample low-priority."""
        if priority in ("critical", "error"):
            return SampledEvent(event_id, data, True, 1.0, priority)
        if priority == "high":
            return SampledEvent(event_id, data, True, 1.0, priority)
        return SampledEvent(event_id, data,
                           self._rng.random() < base_rate,
                           base_rate, priority)

    def reservoir_sample(self, data: dict) -> bool:
        """Reservoir sampling: maintain fixed-size random sample from stream.
        Returns True if event was kept in reservoir."""
        self._stream_count += 1
        if len(self._reservoir) < self._reservoir_size:
            self._reservoir.append(data)
            return True
        # Replace with probability size/count
        j = self._rng.randint(0, self._stream_count - 1)
        if j < self._reservoir_size:
            self._reservoir[j] = data
            return True
        return False

    def get_reservoir(self) -> list[dict]:
        return list(self._reservoir)

    def adaptive_rate(self, target_per_second: float,
                      current_volume: float) -> float:
        """Calculate sampling rate to achieve target throughput.
        If volume = 1000/s and target = 100/s → rate = 0.1."""
        if current_volume <= 0:
            return 1.0
        rate = min(1.0, target_per_second / current_volume)
        return round(rate, 4)

    def weighted_estimate(self, sampled_count: int,
                          sample_rate: float) -> float:
        """Estimate true count from sampled count + rate."""
        if sample_rate <= 0:
            return 0
        return round(sampled_count / sample_rate, 1)

    def reset_reservoir(self, size: int = 100) -> None:
        self._reservoir = []
        self._reservoir_size = size
        self._stream_count = 0
