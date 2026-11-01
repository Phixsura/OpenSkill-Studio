"""App SLI Tracker — track Service Level Indicators.

Manages SLI metrics for installed apps:
- Record SLI measurements (latency p99, availability, throughput)
- Compute SLI over time windows
- Compare against SLO targets
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SLIMeasurement:
    """A single SLI measurement."""

    value: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class SLIReport:
    """SLI report for a metric."""

    metric: str
    current: float
    average: float
    min_val: float
    max_val: float
    measurement_count: int
    meets_target: bool
    target: float | None


class AppSLITracker:
    """Track Service Level Indicators."""

    def __init__(self) -> None:
        # (installation_id, metric) → list[SLIMeasurement]
        self._data: dict[tuple[str, str], list[SLIMeasurement]] = {}
        # (installation_id, metric) → target
        self._targets: dict[tuple[str, str], float] = {}

    def set_target(self, installation_id: str, metric: str, target: float) -> None:
        if not installation_id or not metric:
            raise ValueError("installation_id and metric required")
        self._targets[(installation_id, metric)] = target

    def record(
        self, installation_id: str, metric: str, value: float, now: float | None = None
    ) -> SLIMeasurement:
        if not installation_id:
            raise ValueError("installation_id is required")
        m = SLIMeasurement(value=value, timestamp=now or time.time())
        self._data.setdefault((installation_id, metric), []).append(m)
        return m

    def get_report(self, installation_id: str, metric: str) -> SLIReport:
        key = (installation_id, metric)
        measurements = self._data.get(key, [])
        if not measurements:
            return SLIReport(
                metric=metric, current=0, average=0, min_val=0, max_val=0,
                measurement_count=0, meets_target=True, target=self._targets.get(key),
            )

        values = [m.value for m in measurements]
        avg = sum(values) / len(values)
        target = self._targets.get(key)

        return SLIReport(
            metric=metric, current=values[-1],
            average=round(avg, 2), min_val=min(values), max_val=max(values),
            measurement_count=len(values),
            meets_target=values[-1] >= target if target is not None else True,
            target=target,
        )

    def list_metrics(self, installation_id: str) -> list[str]:
        return sorted({m for (inst, m) in self._data if inst == installation_id})
