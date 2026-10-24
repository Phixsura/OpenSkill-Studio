"""Service config audit — audit configurations for best practices."""
from __future__ import annotations


BEST_PRACTICES = {
    "timeout_configured": "Set explicit request timeouts",
    "retries_configured": "Configure retry policies",
    "circuit_breaker": "Enable circuit breaker",
    "health_check": "Add health check endpoint",
    "logging_structured": "Use structured logging",
    "metrics_enabled": "Enable Prometheus metrics",
    "tracing_enabled": "Enable distributed tracing",
}


def audit_config(service: str, config: dict) -> dict:
    findings = []
    score = 0
    for practice, description in BEST_PRACTICES.items():
        implemented = config.get(practice, False)
        if implemented:
            score += 1
        else:
            findings.append({"practice": practice, "description": description, "status": "missing"})
    total = len(BEST_PRACTICES)
    pct = round(score / total * 100)
    return {"service": service, "score": score, "total": total,
            "compliance_pct": pct, "findings": findings,
            "grade": "A" if pct >= 90 else "B" if pct >= 70 else "C" if pct >= 50 else "D"}
