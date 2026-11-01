"""API Consumer Request Sampling — sample requests for debugging and analytics."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class SampledRequest:
    sample_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    consumer_id: str
    sampled_at: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSampling:
    def __init__(self, sample_rate: float = 0.01, max_samples: int = 5000) -> None:
        if not 0 < sample_rate <= 1: raise ValueError("sample_rate must be 0-1")
        self._rate = sample_rate
        self._max = max(100, max_samples)
        self._samples: dict[str, list[SampledRequest]] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def should_sample(self, request_id: str) -> bool:
        h = int(hashlib.sha256(request_id.encode()).hexdigest()[:8], 16)
        return (h % 10000) < int(self._rate * 10000)

    def record(self, installation_id: str, sample: SampledRequest) -> SampledRequest:
        if not installation_id: raise ValueError("installation_id is required")
        samples = self._samples.setdefault(installation_id, [])
        samples.append(sample)
        if len(samples) > self._max: self._samples[installation_id] = samples[-self._max:]
        stats = self._stats.setdefault(installation_id, {"sampled": 0})
        stats["sampled"] += 1
        return sample

    def recent(self, installation_id: str, limit: int = 20, status_min: int | None = None) -> list[SampledRequest]:
        samples = self._samples.get(installation_id, [])
        if status_min is not None: samples = [s for s in samples if s.status_code >= status_min]
        return list(reversed(samples[-limit:]))

    def sample_count(self, installation_id: str) -> int:
        return len(self._samples.get(installation_id, []))

    def avg_duration(self, installation_id: str) -> float:
        samples = self._samples.get(installation_id, [])
        if not samples: return 0.0
        return round(sum(s.duration_ms for s in samples) / len(samples), 2)
