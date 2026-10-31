"""Consumer API Health Report — periodic health report generation."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class HealthMetric:
    name: str
    value: float
    threshold: float
    status: str = ""  # healthy, warning, critical

    def __post_init__(self):
        if not self.status:
            if self.value <= self.threshold:
                self.status = "healthy"
            elif self.value <= self.threshold * 1.5:
                self.status = "warning"
            else:
                self.status = "critical"


@dataclass
class HealthReport:
    report_id: str
    consumer_id: str
    period: str
    metrics: list[HealthMetric] = field(default_factory=list)
    overall_score: float = 0.0
    recommendations: list[str] = field(default_factory=list)


@dataclass
class HealthReportGenerator:
    """Generate periodic health reports for API consumers."""

    _reports: dict[str, HealthReport] = field(default_factory=dict)

    def generate(self, report_id: str, consumer_id: str, period: str,
                 metrics: list[HealthMetric]) -> dict:
        if report_id in self._reports:
            raise ValueError(f"Report {report_id} already exists")
        if not metrics:
            raise ValueError("At least one metric required")
        # Calculate score
        scores = {"healthy": 100, "warning": 60, "critical": 20}
        avg_score = sum(scores.get(m.status, 0) for m in metrics) / len(metrics)
        # Generate recommendations
        recs = []
        for m in metrics:
            if m.status == "critical":
                recs.append(f"CRITICAL: {m.name} at {m.value} exceeds threshold {m.threshold}")
            elif m.status == "warning":
                recs.append(f"WARNING: {m.name} approaching threshold ({m.value}/{m.threshold})")
        report = HealthReport(
            report_id=report_id, consumer_id=consumer_id, period=period,
            metrics=metrics, overall_score=round(avg_score, 1),
            recommendations=recs,
        )
        self._reports[report_id] = report
        logger.info("health_report_generated", report_id=report_id, score=avg_score)
        return {
            "report_id": report_id, "overall_score": report.overall_score,
            "metrics_count": len(metrics), "recommendations": len(recs),
            "grade": self._grade(avg_score),
        }

    def _grade(self, score: float) -> str:
        if score >= 90: return "A"
        if score >= 75: return "B"
        if score >= 60: return "C"
        if score >= 40: return "D"
        return "F"

    def get_report(self, report_id: str) -> dict | None:
        r = self._reports.get(report_id)
        if not r:
            return None
        return {
            "report_id": r.report_id, "consumer_id": r.consumer_id,
            "period": r.period, "overall_score": r.overall_score,
            "grade": self._grade(r.overall_score),
            "metrics": [{"name": m.name, "value": m.value, "threshold": m.threshold,
                         "status": m.status} for m in r.metrics],
            "recommendations": r.recommendations,
        }

    def list_reports(self, consumer_id: str | None = None) -> list[dict]:
        reports = list(self._reports.values())
        if consumer_id:
            reports = [r for r in reports if r.consumer_id == consumer_id]
        return [{"report_id": r.report_id, "period": r.period,
                 "score": r.overall_score, "grade": self._grade(r.overall_score)}
                for r in reports]

    def compare(self, report_id_a: str, report_id_b: str) -> dict:
        a = self._reports.get(report_id_a)
        b = self._reports.get(report_id_b)
        if not a or not b:
            raise ValueError("Both reports must exist")
        diff = round(b.overall_score - a.overall_score, 1)
        return {
            "from": report_id_a, "to": report_id_b,
            "score_a": a.overall_score, "score_b": b.overall_score,
            "change": diff,
            "trend": "improving" if diff > 0 else "declining" if diff < 0 else "stable",
        }

    def get_stats(self) -> dict:
        reports = list(self._reports.values())
        if not reports:
            return {"total_reports": 0}
        avg = sum(r.overall_score for r in reports) / len(reports)
        return {
            "total_reports": len(reports),
            "avg_score": round(avg, 1),
            "best_score": max(r.overall_score for r in reports),
            "worst_score": min(r.overall_score for r in reports),
        }
