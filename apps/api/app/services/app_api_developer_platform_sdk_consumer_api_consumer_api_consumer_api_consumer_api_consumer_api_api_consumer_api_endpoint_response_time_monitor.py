"""Consumer API Endpoint Response Time Monitor — track response time SLOs."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ResponseTimeTarget:
    endpoint_path: str
    p50_target_ms: float = 100
    p95_target_ms: float = 500
    p99_target_ms: float = 1000

@dataclass
class ResponseTimeSample:
    endpoint_path: str
    latency_ms: float

@dataclass
class ResponseTimeReport:
    endpoint_path: str
    sample_count: int
    p50_ms: float
    p95_ms: float
    p99_ms: float
    p50_ok: bool
    p95_ok: bool
    p99_ok: bool
    all_ok: bool

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerApiEndpointResponseTimeMonitor:
    def __init__(self) -> None:
        self._targets: dict[tuple[str, str], ResponseTimeTarget] = {}
        self._samples: dict[tuple[str, str], list[float]] = {}

    def set_target(self, installation_id: str, target: ResponseTimeTarget) -> ResponseTimeTarget:
        if not installation_id:
            raise ValueError("installation_id is required")
        if target.p50_target_ms > target.p95_target_ms or target.p95_target_ms > target.p99_target_ms:
            raise ValueError("Targets must be in ascending order")
        self._targets[(installation_id, target.endpoint_path)] = target
        return target

    def record_sample(self, installation_id: str, sample: ResponseTimeSample) -> None:
        key = (installation_id, sample.endpoint_path)
        if key not in self._samples:
            self._samples[key] = []
        self._samples[key].append(sample.latency_ms)
        if len(self._samples[key]) > 10000:
            self._samples[key] = self._samples[key][-10000:]

    def get_report(self, installation_id: str, endpoint_path: str) -> ResponseTimeReport:
        key = (installation_id, endpoint_path)
        samples = self._samples.get(key, [])
        target = self._targets.get(key, ResponseTimeTarget(endpoint_path=endpoint_path))
        if not samples:
            return ResponseTimeReport(endpoint_path=endpoint_path, sample_count=0, p50_ms=0, p95_ms=0, p99_ms=0, p50_ok=True, p95_ok=True, p99_ok=True, all_ok=True)
        sorted_s = sorted(samples)
        n = len(sorted_s)
        p50 = sorted_s[int(n * 0.5)]
        p95 = sorted_s[min(int(n * 0.95), n - 1)]
        p99 = sorted_s[min(int(n * 0.99), n - 1)]
        p50_ok = p50 <= target.p50_target_ms
        p95_ok = p95 <= target.p95_target_ms
        p99_ok = p99 <= target.p99_target_ms
        return ResponseTimeReport(endpoint_path=endpoint_path, sample_count=n, p50_ms=round(p50, 1), p95_ms=round(p95, 1), p99_ms=round(p99, 1), p50_ok=p50_ok, p95_ok=p95_ok, p99_ok=p99_ok, all_ok=p50_ok and p95_ok and p99_ok)

    def list_endpoints(self, installation_id: str) -> list[str]:
        return sorted({ep for (inst, ep) in self._targets if inst == installation_id})
