"""App API Developer Webhook Consumer Backpressure — detect and manage delivery backpressure."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class BackpressureState:
    destination: str
    queue_depth: int = 0
    processing_rate_per_sec: float = 0.0
    rejection_count: int = 0
    backpressure_active: bool = False

    @property
    def estimated_drain_seconds(self) -> float:
        if self.processing_rate_per_sec <= 0: return float("inf")
        return round(self.queue_depth / self.processing_rate_per_sec, 1)

    @property
    def pressure_level(self) -> str:
        if self.queue_depth > 10000 or self.rejection_count > 100: return "critical"
        if self.queue_depth > 1000 or self.rejection_count > 10: return "high"
        if self.queue_depth > 100: return "moderate"
        return "normal"

class AppAPIDeveloperPlatformSDKApiPlatformWebhookConsumerBackpressure:
    def __init__(self) -> None:
        self._states: dict[tuple[str, str], BackpressureState] = {}

    def update(self, installation_id: str, destination: str, queue_depth: int, processing_rate: float, rejections: int = 0) -> BackpressureState:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, destination)
        s = BackpressureState(destination=destination, queue_depth=queue_depth, processing_rate_per_sec=processing_rate, rejection_count=rejections, backpressure_active=queue_depth > 1000)
        self._states[key] = s
        return s

    def under_pressure(self, installation_id: str) -> list[BackpressureState]:
        return [s for (inst, _), s in self._states.items() if inst == installation_id and s.pressure_level in ("high", "critical")]

    def all_states(self, installation_id: str) -> list[BackpressureState]:
        return [s for (inst, _), s in self._states.items() if inst == installation_id]
