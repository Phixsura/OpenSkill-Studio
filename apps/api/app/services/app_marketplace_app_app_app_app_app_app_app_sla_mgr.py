"""Service SLA manager — define and track SLAs per service."""
from __future__ import annotations


def define_sla(service: str, targets: dict[str, float]) -> dict:
    return {"service": service, "targets": targets, "metric_count": len(targets)}


def evaluate_sla(sla: dict, actuals: dict[str, float]) -> dict:
    results = []
    met = 0
    for metric, target in sla["targets"].items():
        actual = actuals.get(metric, 0)
        is_met = actual >= target
        if is_met:
            met += 1
        results.append({"metric": metric, "target": target, "actual": actual, "met": is_met})
    total = len(sla["targets"])
    return {"service": sla["service"], "results": results, "met": met,
            "total": total, "compliance_pct": round(met / max(total, 1) * 100),
            "fully_compliant": met == total}


def sla_overview(evaluations: list[dict]) -> dict:
    compliant = sum(1 for e in evaluations if e["fully_compliant"])
    avg_compliance = round(sum(e["compliance_pct"] for e in evaluations) / max(len(evaluations), 1))
    return {"services": len(evaluations), "compliant": compliant,
            "non_compliant": len(evaluations) - compliant,
            "avg_compliance_pct": avg_compliance}
