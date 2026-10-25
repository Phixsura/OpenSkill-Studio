"""SLA Monitor — track and enforce Service Level Agreements for extensions.

Monitors uptime, latency, and error rate against SLA targets,
calculates SLA compliance, and generates violation alerts.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SLATarget:
    extension_id: str
    uptime_target: float = 99.9       # percent
    latency_p99_ms: float = 500.0     # milliseconds
    error_rate_max: float = 1.0       # percent
    resolution_hours: float = 4.0     # max hours to resolve incidents


@dataclass
class SLAMetrics:
    uptime_actual: float = 100.0
    latency_p99_actual: float = 0.0
    error_rate_actual: float = 0.0
    incidents_resolved_within_sla: int = 0
    incidents_total: int = 0


class SLAMonitor:
    """Tracks SLA compliance for extensions."""

    def __init__(self):
        self._targets: dict[str, SLATarget] = {}
        self._metrics: dict[str, SLAMetrics] = {}
        self._violations: list[dict] = []

    def set_target(self, target: SLATarget) -> None:
        self._targets[target.extension_id] = target

    def update_metrics(self, extension_id: str, metrics: SLAMetrics) -> None:
        self._metrics[extension_id] = metrics

    def check_compliance(self, extension_id: str) -> dict:
        """Check if extension meets its SLA targets."""
        target = self._targets.get(extension_id)
        metrics = self._metrics.get(extension_id)
        if not target or not metrics:
            return {"extension_id": extension_id, "status": "no_data"}

        checks = {
            "uptime": {
                "target": target.uptime_target,
                "actual": metrics.uptime_actual,
                "met": metrics.uptime_actual >= target.uptime_target,
                "delta": round(metrics.uptime_actual - target.uptime_target, 3),
            },
            "latency_p99": {
                "target": target.latency_p99_ms,
                "actual": metrics.latency_p99_actual,
                "met": metrics.latency_p99_actual <= target.latency_p99_ms,
            },
            "error_rate": {
                "target": target.error_rate_max,
                "actual": metrics.error_rate_actual,
                "met": metrics.error_rate_actual <= target.error_rate_max,
            },
        }

        all_met = all(c["met"] for c in checks.values())
        violations = [name for name, c in checks.items() if not c["met"]]

        if violations:
            for v in violations:
                self._violations.append({
                    "extension_id": extension_id, "metric": v,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

        return {
            "extension_id": extension_id,
            "compliant": all_met,
            "checks": checks,
            "violations": violations,
            "sla_score": round(sum(1 for c in checks.values() if c["met"]) / len(checks) * 100, 1),
        }

    def get_sla_report(self, extension_id: str) -> dict:
        compliance = self.check_compliance(extension_id)
        ext_violations = [v for v in self._violations if v["extension_id"] == extension_id]
        return {
            **compliance,
            "total_violations": len(ext_violations),
            "metrics_period": "current",
        }

    def get_violations(self, extension_id: str | None = None) -> list[dict]:
        if extension_id:
            return [v for v in self._violations if v["extension_id"] == extension_id]
        return list(self._violations)

    def get_compliance_summary(self) -> dict:
        results = {}
        for ext_id in self._targets:
            comp = self.check_compliance(ext_id)
            results[ext_id] = comp.get("compliant", False)
        total = len(results)
        compliant = sum(1 for v in results.values() if v)
        return {
            "total_extensions": total,
            "compliant": compliant,
            "non_compliant": total - compliant,
            "compliance_rate": round(compliant / max(1, total) * 100, 1),
        }
