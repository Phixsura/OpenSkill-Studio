"""App Canary Release — gradual rollout with traffic splitting.

Manages canary deployments for installed apps:
- Define canary releases with traffic percentage
- Track canary vs stable metrics
- Promote or rollback canary
- Per-installation scoped releases
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class CanaryStatus(str, Enum):
    ACTIVE = "active"
    PROMOTED = "promoted"
    ROLLED_BACK = "rolled_back"


@dataclass
class CanaryRelease:
    """A canary release configuration."""

    release_id: str
    installation_id: str
    stable_version: str
    canary_version: str
    traffic_pct: float  # 0-100, % routed to canary
    status: CanaryStatus = CanaryStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    decided_at: float | None = None
    stable_error_rate: float = 0.0
    canary_error_rate: float = 0.0
    stable_latency_ms: float = 0.0
    canary_latency_ms: float = 0.0


class AppCanaryRelease:
    """Gradual rollout with traffic splitting."""

    def __init__(self) -> None:
        self._releases: dict[tuple[str, str], CanaryRelease] = {}

    def create_release(
        self,
        installation_id: str,
        release_id: str,
        stable_version: str,
        canary_version: str,
        traffic_pct: float = 5.0,
        now: float | None = None,
    ) -> CanaryRelease:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not release_id:
            raise ValueError("release_id is required")
        if not (0 < traffic_pct <= 100):
            raise ValueError("traffic_pct must be between 0 and 100")
        if stable_version == canary_version:
            raise ValueError("canary must differ from stable")

        key = (installation_id, release_id)
        if key in self._releases:
            raise ValueError(f"Release {release_id} already exists")

        release = CanaryRelease(
            release_id=release_id,
            installation_id=installation_id,
            stable_version=stable_version,
            canary_version=canary_version,
            traffic_pct=traffic_pct,
            created_at=now or time.time(),
        )
        self._releases[key] = release
        return release

    def update_traffic(
        self, installation_id: str, release_id: str, traffic_pct: float
    ) -> CanaryRelease:
        r = self._get(installation_id, release_id)
        if r.status != CanaryStatus.ACTIVE:
            raise ValueError("Cannot update traffic on non-active release")
        if not (0 < traffic_pct <= 100):
            raise ValueError("traffic_pct must be between 0 and 100")
        r.traffic_pct = traffic_pct
        return r

    def record_metrics(
        self,
        installation_id: str,
        release_id: str,
        stable_error_rate: float = 0.0,
        canary_error_rate: float = 0.0,
        stable_latency_ms: float = 0.0,
        canary_latency_ms: float = 0.0,
    ) -> CanaryRelease:
        r = self._get(installation_id, release_id)
        r.stable_error_rate = stable_error_rate
        r.canary_error_rate = canary_error_rate
        r.stable_latency_ms = stable_latency_ms
        r.canary_latency_ms = canary_latency_ms
        return r

    def promote(self, installation_id: str, release_id: str) -> CanaryRelease:
        """Promote canary to 100% (replace stable)."""
        r = self._get(installation_id, release_id)
        if r.status != CanaryStatus.ACTIVE:
            raise ValueError("Can only promote active releases")
        r.status = CanaryStatus.PROMOTED
        r.traffic_pct = 100.0
        r.decided_at = time.time()
        return r

    def rollback(self, installation_id: str, release_id: str) -> CanaryRelease:
        """Roll back canary to 0% (keep stable)."""
        r = self._get(installation_id, release_id)
        if r.status != CanaryStatus.ACTIVE:
            raise ValueError("Can only rollback active releases")
        r.status = CanaryStatus.ROLLED_BACK
        r.traffic_pct = 0.0
        r.decided_at = time.time()
        return r

    def get_release(self, installation_id: str, release_id: str) -> CanaryRelease:
        return self._get(installation_id, release_id)

    def list_releases(self, installation_id: str) -> list[CanaryRelease]:
        return [r for (inst, _), r in self._releases.items() if inst == installation_id]

    def _get(self, installation_id: str, release_id: str) -> CanaryRelease:
        key = (installation_id, release_id)
        r = self._releases.get(key)
        if r is None:
            raise KeyError(f"Release {release_id} not found")
        return r
