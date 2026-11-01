"""App API Developer API Request Rate Monitor — real-time request rate monitoring."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RequestRate:
    endpoint: str
    current_rps: float = 0.0
    avg_rps: float = 0.0
    peak_rps: float = 0.0
    samples: int = 0

    @property
    def load_level(self) -> str:
        if self.current_rps > self.avg_rps * 3: return "spike"
        if self.current_rps > self.avg_rps * 1.5: return "high"
        if self.current_rps < self.avg_rps * 0.3 and self.avg_rps > 0: return "low"
        return "normal"

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitor:
    def __init__(self) -> None:
        self._rates: dict[tuple[str, str], RequestRate] = {}

    def record(self, installation_id: str, endpoint: str, rps: float) -> RequestRate:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        if key not in self._rates:
            self._rates[key] = RequestRate(endpoint=endpoint)
        r = self._rates[key]
        r.current_rps = rps
        if rps > r.peak_rps: r.peak_rps = rps
        r.samples += 1
        r.avg_rps = round(((r.avg_rps * (r.samples - 1)) + rps) / r.samples, 1)
        return r

    def spikes(self, installation_id: str) -> list[RequestRate]:
        return [r for (inst, _), r in self._rates.items() if inst == installation_id and r.load_level == "spike"]

    def all_rates(self, installation_id: str) -> list[RequestRate]:
        return sorted([r for (inst, _), r in self._rates.items() if inst == installation_id], key=lambda r: r.current_rps, reverse=True)
