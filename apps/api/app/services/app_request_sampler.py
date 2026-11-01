"""App Request Sampler — sample and store request/response pairs for debugging.

Manages request sampling for installed apps:
- Sample requests based on rate
- Store request/response pairs
- Query samples by endpoint
- Per-installation scoped samples
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SampledRequest:
    """A sampled request/response pair."""

    sample_id: str
    method: str
    path: str
    status_code: int
    request_headers: dict = field(default_factory=dict)
    response_body_preview: str = ""
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


class AppRequestSampler:
    """Sample and store request/response pairs."""

    def __init__(self, max_samples: int = 500, sample_rate: float = 0.1) -> None:
        if not 0 < sample_rate <= 1:
            raise ValueError("sample_rate must be between 0 and 1")
        self._max = max(1, max_samples)
        self._rate = sample_rate
        self._samples: dict[str, list[SampledRequest]] = {}

    def should_sample(self, request_id: str) -> bool:
        """Deterministic sampling based on request ID hash."""
        h = int(hashlib.sha256(request_id.encode()).hexdigest()[:8], 16)
        return (h % 10000) < (self._rate * 10000)

    _SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key",
                          "proxy-authorization", "x-auth-token"}

    def _scrub_headers(self, headers: dict) -> dict:
        return {
            k: ("[REDACTED]" if k.lower() in self._SENSITIVE_HEADERS
                or any(t in k.lower() for t in ("token", "secret", "key", "password"))
                else v)
            for k, v in headers.items()
        }

    def store_sample(
        self,
        installation_id: str,
        sample: SampledRequest,
    ) -> SampledRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        # Scrub sensitive headers before storing
        sample.request_headers = self._scrub_headers(sample.request_headers)
        samples = self._samples.setdefault(installation_id, [])
        samples.append(sample)
        if len(samples) > self._max:
            self._samples[installation_id] = samples[-self._max:]
        return sample

    def get_samples(
        self,
        installation_id: str,
        method: str | None = None,
        path: str | None = None,
        status_min: int | None = None,
        limit: int = 20,
    ) -> list[SampledRequest]:
        samples = self._samples.get(installation_id, [])
        if method:
            samples = [s for s in samples if s.method == method.upper()]
        if path:
            samples = [s for s in samples if s.path == path]
        if status_min is not None:
            samples = [s for s in samples if s.status_code >= status_min]
        return list(reversed(samples[-limit:]))

    def sample_count(self, installation_id: str) -> int:
        return len(self._samples.get(installation_id, []))
