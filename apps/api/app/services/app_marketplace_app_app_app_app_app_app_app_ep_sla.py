"""API endpoint SLA tracker — track SLA compliance per endpoint."""
from __future__ import annotations


def check_endpoint_sla(endpoint: str, metrics: dict, targets: dict) -> dict:
    checks = {}
    checks["availability"] = metrics.get("availability_pct", 100) >= targets.get("availability", 99.9)
    checks["latency"] = metrics.get("p99_ms", 0) <= targets.get("max_p99_ms", 500)
    checks["error_rate"] = metrics.get("error_rate_pct", 0) <= targets.get("max_error_pct", 1)
    compliant = all(checks.values())
    return {"endpoint": endpoint, "compliant": compliant, "checks": checks,
            "metrics": metrics, "targets": targets}


def sla_report(endpoints: list[dict]) -> dict:
    compliant = sum(1 for e in endpoints if e["compliant"])
    return {"total": len(endpoints), "compliant": compliant,
            "non_compliant": len(endpoints) - compliant,
            "compliance_pct": round(compliant / max(len(endpoints), 1) * 100, 1)}
