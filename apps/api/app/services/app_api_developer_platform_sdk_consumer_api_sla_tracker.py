"""Consumer SLA Tracker — SLA compliance monitoring with breach detection."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class SlaTarget:
    sla_id: str
    consumer_id: str
    metric: str  # uptime_pct, latency_p99_ms, error_rate_pct
    target_value: float
    operator: str = "lte"  # lte, gte, lt, gt

    def is_met(self, actual: float) -> bool:
        if self.operator == "lte":
            return actual <= self.target_value
        elif self.operator == "gte":
            return actual >= self.target_value
        elif self.operator == "lt":
            return actual < self.target_value
        elif self.operator == "gt":
            return actual > self.target_value
        return False


@dataclass
class SlaReport:
    sla_id: str
    actual_value: float
    target_value: float
    met: bool
    period: str


@dataclass
class SlaTracker:
    """Track SLA compliance and detect breaches."""

    _targets: dict[str, SlaTarget] = field(default_factory=dict)
    _reports: list[SlaReport] = field(default_factory=list)

    def define_sla(self, target: SlaTarget) -> dict:
        if target.operator not in ("lte", "gte", "lt", "gt"):
            raise ValueError(f"Invalid operator: {target.operator}")
        self._targets[target.sla_id] = target
        logger.info("sla_defined", sla_id=target.sla_id, metric=target.metric)
        return {"sla_id": target.sla_id, "metric": target.metric,
                "target": target.target_value, "operator": target.operator}

    def record(self, sla_id: str, actual_value: float, period: str) -> dict:
        target = self._targets.get(sla_id)
        if not target:
            raise ValueError(f"SLA {sla_id} not defined")
        met = target.is_met(actual_value)
        report = SlaReport(sla_id=sla_id, actual_value=actual_value,
                           target_value=target.target_value, met=met, period=period)
        self._reports.append(report)
        if not met:
            logger.warning("sla_breach", sla_id=sla_id, actual=actual_value,
                           target=target.target_value, period=period)
        return {"sla_id": sla_id, "met": met, "actual": actual_value,
                "target": target.target_value, "period": period}

    def get_compliance(self, sla_id: str) -> dict:
        reports = [r for r in self._reports if r.sla_id == sla_id]
        if not reports:
            return {"sla_id": sla_id, "status": "no_data"}
        met_count = sum(1 for r in reports if r.met)
        total = len(reports)
        compliance_pct = round(met_count / total * 100, 1)
        breaches = [{"period": r.period, "actual": r.actual_value, "target": r.target_value}
                    for r in reports if not r.met]
        return {
            "sla_id": sla_id,
            "compliance_pct": compliance_pct,
            "met_count": met_count,
            "total_periods": total,
            "breach_count": len(breaches),
            "recent_breaches": breaches[-5:],
            "status": "compliant" if compliance_pct >= 99 else
                      "at_risk" if compliance_pct >= 95 else "breached",
        }

    def get_consumer_summary(self, consumer_id: str) -> dict:
        slas = [t for t in self._targets.values() if t.consumer_id == consumer_id]
        results = []
        for sla in slas:
            compliance = self.get_compliance(sla.sla_id)
            results.append({
                "sla_id": sla.sla_id,
                "metric": sla.metric,
                "target": sla.target_value,
                "status": compliance.get("status", "no_data"),
                "compliance_pct": compliance.get("compliance_pct", 0),
            })
        overall = "compliant"
        for r in results:
            if r["status"] == "breached":
                overall = "breached"
                break
            elif r["status"] == "at_risk":
                overall = "at_risk"
        return {"consumer_id": consumer_id, "sla_count": len(results),
                "overall_status": overall, "slas": results}

    def list_breaches(self, limit: int = 20) -> list[dict]:
        breaches = [r for r in self._reports if not r.met]
        return [
            {"sla_id": r.sla_id, "period": r.period, "actual": r.actual_value,
             "target": r.target_value}
            for r in breaches[-limit:]
        ]
