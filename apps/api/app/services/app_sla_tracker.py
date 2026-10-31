"""App SLA Tracker — track service level agreement compliance.

Monitors SLA targets for installed apps:
- Define SLA targets (uptime %, response time, error rate)
- Record measurements against targets
- Compute compliance over time windows
- Track SLA breaches
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SLATarget:
    """An SLA target definition."""

    target_id: str
    name: str
    metric: str  # "uptime_pct", "response_time_ms", "error_rate_pct"
    threshold: float  # target value
    comparison: str = "gte"  # "gte" (>=), "lte" (<=)


@dataclass
class SLAMeasurement:
    """A single SLA measurement."""

    value: float
    timestamp: float = field(default_factory=time.time)
    met: bool = True


@dataclass
class SLAStatus:
    """Current SLA compliance status."""

    target: SLATarget
    current_value: float
    met: bool
    measurements: int
    compliance_pct: float  # % of measurements meeting SLA
    breaches: int


class AppSLATracker:
    """Track SLA compliance for installed apps."""

    def __init__(self) -> None:
        # (installation_id, target_id) → SLATarget
        self._targets: dict[tuple[str, str], SLATarget] = {}
        # (installation_id, target_id) → list[SLAMeasurement]
        self._measurements: dict[tuple[str, str], list[SLAMeasurement]] = {}

    def define_target(
        self,
        installation_id: str,
        target_id: str,
        name: str,
        metric: str,
        threshold: float,
        comparison: str = "gte",
    ) -> SLATarget:
        """Define an SLA target."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not target_id:
            raise ValueError("target_id is required")
        if comparison not in ("gte", "lte"):
            raise ValueError("comparison must be 'gte' or 'lte'")

        target = SLATarget(
            target_id=target_id, name=name, metric=metric,
            threshold=threshold, comparison=comparison,
        )
        key = (installation_id, target_id)
        self._targets[key] = target
        self._measurements.setdefault(key, [])
        return target

    def record(
        self,
        installation_id: str,
        target_id: str,
        value: float,
        now: float | None = None,
    ) -> SLAMeasurement:
        """Record a measurement against an SLA target."""
        key = (installation_id, target_id)
        target = self._targets.get(key)
        if target is None:
            raise KeyError(f"Target {target_id} not found")

        met = self._check(target, value)
        measurement = SLAMeasurement(
            value=value, timestamp=now or time.time(), met=met,
        )
        self._measurements[key].append(measurement)

        if not met:
            log.warning("sla.breach", target_id=target_id, value=value,
                         threshold=target.threshold)

        return measurement

    def get_status(self, installation_id: str, target_id: str) -> SLAStatus:
        """Get current SLA status."""
        key = (installation_id, target_id)
        target = self._targets.get(key)
        if target is None:
            raise KeyError(f"Target {target_id} not found")

        measurements = self._measurements.get(key, [])
        total = len(measurements)
        met_count = sum(1 for m in measurements if m.met)
        breaches = total - met_count
        compliance = (met_count / total * 100) if total > 0 else 100.0
        current = measurements[-1].value if measurements else 0.0

        return SLAStatus(
            target=target,
            current_value=current,
            met=self._check(target, current) if measurements else True,
            measurements=total,
            compliance_pct=round(compliance, 2),
            breaches=breaches,
        )

    def list_targets(self, installation_id: str) -> list[SLATarget]:
        return [
            t for (inst, _), t in self._targets.items()
            if inst == installation_id
        ]

    def _check(self, target: SLATarget, value: float) -> bool:
        if target.comparison == "gte":
            return value >= target.threshold
        return value <= target.threshold
