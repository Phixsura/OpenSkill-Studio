"""SLA compliance tracker — monitor uptime and response time against targets."""
from __future__ import annotations


def check_sla_compliance(*, uptime_pct: float, target_uptime: float = 99.9,
                          avg_response_ms: float, target_response_ms: float = 200,
                          p99_response_ms: float = 0, target_p99_ms: float = 1000,
                          incidents: int = 0, max_incidents: int = 3,
                          period: str = "monthly") -> dict:
    checks = [
        {"metric": "uptime", "actual": uptime_pct, "target": target_uptime,
         "unit": "%", "passed": uptime_pct >= target_uptime},
        {"metric": "avg_response", "actual": avg_response_ms, "target": target_response_ms,
         "unit": "ms", "passed": avg_response_ms <= target_response_ms},
        {"metric": "p99_response", "actual": p99_response_ms, "target": target_p99_ms,
         "unit": "ms", "passed": p99_response_ms <= target_p99_ms},
        {"metric": "incidents", "actual": incidents, "target": max_incidents,
         "unit": "count", "passed": incidents <= max_incidents},
    ]
    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    compliant = all(c["passed"] for c in checks)
    score = round(passed / total * 100)
    return {
        "compliant": compliant, "score": score, "score_display": f"{score}%",
        "status": "compliant" if compliant else "breached",
        "period": period, "checks": checks,
        "passed": passed, "total": total,
        "credit_due": not compliant and uptime_pct < target_uptime,
    }
