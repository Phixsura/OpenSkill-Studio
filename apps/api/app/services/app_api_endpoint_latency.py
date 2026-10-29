"""App API Endpoint Latency — per-endpoint latency tracking."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointLatency:
    method: str
    path: str
    samples: list[float] = field(default_factory=list)

    @property
    def avg(self) -> float:
        if not self.samples: return 0.0
        return round(sum(self.samples) / len(self.samples), 1)

    @property
    def p99(self) -> float:
        if not self.samples: return 0.0
        s = sorted(self.samples)
        return s[int(len(s) * 0.99)]

class AppAPIEndpointLatency:
    def __init__(self, max_samples: int = 500) -> None:
        self._max = max_samples
        self._data: dict[tuple[str, str, str], EndpointLatency] = {}

    def record(self, installation_id: str, method: str, path: str, latency_ms: float) -> EndpointLatency:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), path)
        if key not in self._data:
            self._data[key] = EndpointLatency(method=method.upper(), path=path)
        el = self._data[key]
        el.samples.append(latency_ms)
        if len(el.samples) > self._max:
            el.samples = el.samples[-self._max:]
        return el

    def slowest(self, installation_id: str, limit: int = 10) -> list[EndpointLatency]:
        eps = [el for (inst, _, _), el in self._data.items() if inst == installation_id]
        return sorted(eps, key=lambda e: e.avg, reverse=True)[:limit]

    def list_endpoints(self, installation_id: str) -> list[EndpointLatency]:
        return [el for (inst, _, _), el in self._data.items() if inst == installation_id]
