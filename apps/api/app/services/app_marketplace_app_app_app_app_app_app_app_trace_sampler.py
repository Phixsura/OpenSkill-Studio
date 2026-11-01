"""Distributed tracing sampler — adaptive sampling based on traffic."""
from __future__ import annotations
import hashlib


class AdaptiveSampler:
    def __init__(self, base_rate: float = 0.1, min_rate: float = 0.01, max_rate: float = 1.0):
        self._base_rate = base_rate
        self._min_rate = min_rate
        self._max_rate = max_rate
        self._current_rate = base_rate
        self._sampled = 0
        self._total = 0

    def should_sample(self, trace_id: str) -> dict:
        self._total += 1
        h = int(hashlib.md5(trace_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        sampled = h < self._current_rate
        if sampled:
            self._sampled += 1
        return {"sample": sampled, "rate": self._current_rate, "trace_id": trace_id}

    def adapt(self, current_rps: float, target_samples_per_sec: float = 10) -> dict:
        if current_rps > 0:
            desired_rate = target_samples_per_sec / current_rps
            self._current_rate = max(self._min_rate, min(self._max_rate, desired_rate))
        return {"new_rate": round(self._current_rate, 4), "rps": current_rps}

    def stats(self) -> dict:
        actual_rate = round(self._sampled / max(self._total, 1) * 100, 2)
        return {"sampled": self._sampled, "total": self._total,
                "actual_rate_pct": actual_rate, "current_rate": self._current_rate}
