"""Span sampler — configurable trace sampling strategies."""
from __future__ import annotations
import hashlib


class SpanSampler:
    def __init__(self, rate: float = 1.0, strategy: str = "probabilistic"):
        self._rate = min(1.0, max(0.0, rate))
        self._strategy = strategy
        self._sampled = 0
        self._dropped = 0

    def should_sample(self, trace_id: str) -> dict:
        if self._strategy == "always":
            self._sampled += 1
            return {"sample": True, "strategy": "always"}
        if self._strategy == "never":
            self._dropped += 1
            return {"sample": False, "strategy": "never"}
        h = int(hashlib.md5(trace_id.encode()).hexdigest()[:8], 16)
        pct = h / 0xFFFFFFFF
        sampled = pct < self._rate
        if sampled:
            self._sampled += 1
        else:
            self._dropped += 1
        return {"sample": sampled, "strategy": self._strategy, "rate": self._rate}

    def stats(self) -> dict:
        total = self._sampled + self._dropped
        actual_rate = round(self._sampled / max(total, 1) * 100, 1)
        return {"sampled": self._sampled, "dropped": self._dropped,
                "total": total, "actual_rate_pct": actual_rate,
                "configured_rate": self._rate}
