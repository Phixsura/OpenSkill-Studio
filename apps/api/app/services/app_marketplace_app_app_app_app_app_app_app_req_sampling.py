"""Request sampling controller — sample requests for debugging and analysis."""
from __future__ import annotations
import hashlib


class RequestSampler:
    def __init__(self, sample_rate: float = 0.01):
        self._rate = sample_rate
        self._sampled: list[dict] = []
        self._total = 0

    def should_sample(self, request_id: str) -> bool:
        self._total += 1
        h = int(hashlib.md5(request_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        return h < self._rate

    def capture(self, request: dict) -> dict:
        self._sampled.append(request)
        if len(self._sampled) > 1000:
            self._sampled = self._sampled[-1000:]
        return {"captured": True, "buffer_size": len(self._sampled)}

    def recent(self, limit: int = 20) -> list[dict]:
        return self._sampled[-limit:]

    def stats(self) -> dict:
        return {"total_seen": self._total, "captured": len(self._sampled),
                "sample_rate": self._rate}
