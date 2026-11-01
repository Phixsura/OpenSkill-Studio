"""Consumer API Endpoint Canary Release — gradual endpoint rollout with canary analysis."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class CanaryRelease:
    release_id: str
    endpoint_path: str
    canary_version: str
    stable_version: str
    canary_weight_pct: int = 5  # 0-100
    status: str = "active"  # "active", "promoting", "promoted", "rolled_back"
    created_at: datetime | None = None

@dataclass
class CanaryMetrics:
    canary_error_rate: float
    stable_error_rate: float
    canary_latency_ms: float
    stable_latency_ms: float
    canary_requests: int
    stable_requests: int

@dataclass
class CanaryAnalysis:
    safe_to_promote: bool
    error_rate_delta: float
    latency_delta_ms: float
    recommendation: str

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease:
    def __init__(self) -> None:
        self._releases: dict[tuple[str, str], CanaryRelease] = {}

    def create(self, installation_id: str, release: CanaryRelease) -> CanaryRelease:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (0 <= release.canary_weight_pct <= 100):
            raise ValueError("canary_weight_pct must be 0-100")
        release.created_at = release.created_at or datetime.utcnow()
        release.status = "active"
        self._releases[(installation_id, release.release_id)] = release
        return release

    def update_weight(self, installation_id: str, release_id: str, new_weight: int) -> CanaryRelease:
        key = (installation_id, release_id)
        release = self._releases.get(key)
        if not release:
            raise ValueError("Release not found")
        if not (0 <= new_weight <= 100):
            raise ValueError("Weight must be 0-100")
        release.canary_weight_pct = new_weight
        return release

    def analyze(self, metrics: CanaryMetrics) -> CanaryAnalysis:
        err_delta = metrics.canary_error_rate - metrics.stable_error_rate
        lat_delta = metrics.canary_latency_ms - metrics.stable_latency_ms
        safe = err_delta <= 0.5 and lat_delta <= 50  # thresholds
        if safe:
            rec = "Safe to promote — canary metrics within thresholds"
        elif err_delta > 2:
            rec = "ROLL BACK — canary error rate significantly higher"
        else:
            rec = "Monitor — canary showing slight degradation"
        return CanaryAnalysis(safe_to_promote=safe, error_rate_delta=round(err_delta, 2), latency_delta_ms=round(lat_delta, 1), recommendation=rec)

    def promote(self, installation_id: str, release_id: str) -> CanaryRelease:
        key = (installation_id, release_id)
        release = self._releases.get(key)
        if not release:
            raise ValueError("Release not found")
        release.status = "promoted"
        release.canary_weight_pct = 100
        return release

    def rollback(self, installation_id: str, release_id: str) -> CanaryRelease:
        key = (installation_id, release_id)
        release = self._releases.get(key)
        if not release:
            raise ValueError("Release not found")
        release.status = "rolled_back"
        release.canary_weight_pct = 0
        return release

    def list_active(self, installation_id: str) -> list[CanaryRelease]:
        return [r for (inst, _), r in self._releases.items() if inst == installation_id and r.status == "active"]
