"""App API Developer Platform Release Impact — measure the impact of API releases."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ReleaseImpact:
    version: str
    error_rate_before: float
    error_rate_after: float
    latency_before_ms: float
    latency_after_ms: float
    consumers_affected: int = 0
    breaking_changes: int = 0
    rollback_needed: bool = False

    @property
    def error_delta(self) -> float:
        return round(self.error_rate_after - self.error_rate_before, 2)

    @property
    def latency_delta_ms(self) -> float:
        return round(self.latency_after_ms - self.latency_before_ms, 1)

    @property
    def impact_severity(self) -> str:
        if self.rollback_needed: return "critical"
        if self.error_delta > 1 or self.latency_delta_ms > 100: return "high"
        if self.error_delta > 0.1 or self.latency_delta_ms > 20: return "medium"
        return "low"

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpact:
    def __init__(self) -> None:
        self._impacts: dict[tuple[str, str], ReleaseImpact] = {}

    def record(self, installation_id: str, version: str, **kwargs) -> ReleaseImpact:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, version)
        r = ReleaseImpact(version=version, error_rate_before=kwargs.get("error_rate_before", 0), error_rate_after=kwargs.get("error_rate_after", 0), latency_before_ms=kwargs.get("latency_before_ms", 0), latency_after_ms=kwargs.get("latency_after_ms", 0))
        for k, v in kwargs.items():
            if hasattr(r, k): setattr(r, k, v)
        self._impacts[key] = r
        return r

    def high_impact_releases(self, installation_id: str) -> list[ReleaseImpact]:
        return [r for (inst, _), r in self._impacts.items() if inst == installation_id and r.impact_severity in ("high", "critical")]

    def all_impacts(self, installation_id: str) -> list[ReleaseImpact]:
        return [r for (inst, _), r in self._impacts.items() if inst == installation_id]
