"""App API Developer Platform Health Index — single composite health number for the platform."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PlatformHealthIndex:
    # Inputs (0-100 each)
    availability_score: float = 100
    latency_score: float = 100
    error_rate_score: float = 100
    webhook_score: float = 100
    security_score: float = 100
    dx_score: float = 100

    @property
    def index(self) -> float:
        weights = [(self.availability_score, 0.25), (self.latency_score, 0.15), (self.error_rate_score, 0.20), (self.webhook_score, 0.15), (self.security_score, 0.15), (self.dx_score, 0.10)]
        return round(sum(s * w for s, w in weights), 1)

    @property
    def grade(self) -> str:
        i = self.index
        if i >= 95: return "A+"
        if i >= 90: return "A"
        if i >= 85: return "B+"
        if i >= 80: return "B"
        if i >= 70: return "C"
        if i >= 60: return "D"
        return "F"

    @property
    def trend_emoji(self) -> str:
        i = self.index
        if i >= 90: return "🟢"
        if i >= 75: return "🟡"
        return "🔴"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndex:
    def __init__(self) -> None:
        self._indices: dict[str, PlatformHealthIndex] = {}

    def update(self, installation_id: str, **kwargs) -> PlatformHealthIndex:
        if not installation_id: raise ValueError("installation_id is required")
        h = PlatformHealthIndex()
        for k, v in kwargs.items():
            if hasattr(h, k): setattr(h, k, v)
        self._indices[installation_id] = h
        return h

    def get(self, installation_id: str) -> PlatformHealthIndex:
        return self._indices.get(installation_id, PlatformHealthIndex())
