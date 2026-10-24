"""Deployment confidence score — assess deployment risk before releasing."""
from __future__ import annotations


def calculate_confidence(checks: dict) -> dict:
    weights = {"tests_passing": 25, "coverage_above_80": 15, "no_critical_vulns": 20,
               "canary_healthy": 15, "rollback_tested": 10, "monitoring_ready": 10,
               "approval_received": 5}
    score = 0
    results = []
    for check, weight in weights.items():
        passed = checks.get(check, False)
        if passed:
            score += weight
        results.append({"check": check, "weight": weight, "passed": passed})
    risk = "low" if score >= 85 else "medium" if score >= 60 else "high"
    return {"confidence_score": score, "risk_level": risk, "checks": results,
            "deploy_recommended": score >= 75, "max_score": 100}
