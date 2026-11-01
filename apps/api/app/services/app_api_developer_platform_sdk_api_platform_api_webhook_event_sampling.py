"""App API Developer Webhook Event Sampling — sample webhook events for debugging."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class SampledEvent:
    event_id: str
    event_type: str
    destination: str
    payload_preview: str
    status_code: int
    latency_ms: float

class AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventSampling:
    def __init__(self, sample_rate: float = 0.01, max_samples: int = 1000) -> None:
        if not 0 < sample_rate <= 1: raise ValueError("sample_rate must be 0-1")
        self._rate = sample_rate
        self._max = max(1, max_samples)
        self._samples: dict[str, list[SampledEvent]] = {}

    def should_sample(self, event_id: str) -> bool:
        h = int(hashlib.sha256(event_id.encode()).hexdigest()[:8], 16)
        return (h % 10000) < int(self._rate * 10000)

    def store(self, installation_id: str, event_id: str, event_type: str, destination: str, payload_preview: str, status_code: int, latency_ms: float) -> SampledEvent:
        if not installation_id: raise ValueError("installation_id is required")
        s = SampledEvent(event_id=event_id, event_type=event_type, destination=destination, payload_preview=payload_preview[:500], status_code=status_code, latency_ms=latency_ms)
        samples = self._samples.setdefault(installation_id, [])
        samples.append(s)
        if len(samples) > self._max: self._samples[installation_id] = samples[-self._max:]
        return s

    def recent(self, installation_id: str, limit: int = 20) -> list[SampledEvent]:
        return list(reversed(self._samples.get(installation_id, [])[-limit:]))

    def by_status(self, installation_id: str, min_status: int) -> list[SampledEvent]:
        return [s for s in self._samples.get(installation_id, []) if s.status_code >= min_status]

    def count(self, installation_id: str) -> int:
        return len(self._samples.get(installation_id, []))
