"""App Health Score — compute an overall health score from multiple signals.

Computes a weighted health score for installed apps:
- Combine metrics: uptime, error rate, latency, saturation
- Weighted scoring (0-100)
- Health grade (A/B/C/D/F)
- Signal breakdown
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class HealthSignal:
    """A health signal with its score."""

    name: str
    value: float       # raw metric value
    score: float       # normalized 0-100
    weight: float = 1.0
    status: str = "ok"  # ok, degraded, critical


@dataclass
class HealthReport:
    """Overall health report."""

    overall_score: float
    grade: str
    signals: list[HealthSignal]


class AppHealthScore:
    """Compute weighted health scores from multiple signals."""

    def __init__(self) -> None:
        pass

    def compute(
        self,
        uptime_pct: float = 100.0,
        error_rate_pct: float = 0.0,
        avg_latency_ms: float = 0.0,
        saturation_pct: float = 0.0,
        weights: dict[str, float] | None = None,
    ) -> HealthReport:
        """Compute health score from signals."""
        w = weights or {
            "uptime": 3.0,
            "error_rate": 2.0,
            "latency": 1.5,
            "saturation": 1.0,
        }

        signals = [
            HealthSignal(
                name="uptime", value=uptime_pct,
                score=min(100, uptime_pct),
                weight=w.get("uptime", 3.0),
                status=self._status(uptime_pct, 99.9, 99.0),
            ),
            HealthSignal(
                name="error_rate", value=error_rate_pct,
                score=max(0, 100 - error_rate_pct * 10),
                weight=w.get("error_rate", 2.0),
                status=self._status_inverse(error_rate_pct, 1.0, 5.0),
            ),
            HealthSignal(
                name="latency", value=avg_latency_ms,
                score=max(0, 100 - avg_latency_ms / 10),
                weight=w.get("latency", 1.5),
                status=self._status_inverse(avg_latency_ms, 200, 1000),
            ),
            HealthSignal(
                name="saturation", value=saturation_pct,
                score=max(0, 100 - saturation_pct),
                weight=w.get("saturation", 1.0),
                status=self._status_inverse(saturation_pct, 70, 90),
            ),
        ]

        total_weight = sum(s.weight for s in signals)
        weighted_sum = sum(s.score * s.weight for s in signals)
        overall = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0

        return HealthReport(
            overall_score=overall,
            grade=self._grade(overall),
            signals=signals,
        )

    def _status(self, value: float, good_threshold: float, warn_threshold: float) -> str:
        if value >= good_threshold:
            return "ok"
        if value >= warn_threshold:
            return "degraded"
        return "critical"

    def _status_inverse(self, value: float, warn_threshold: float, critical_threshold: float) -> str:
        if value <= warn_threshold:
            return "ok"
        if value <= critical_threshold:
            return "degraded"
        return "critical"

    def _grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"
