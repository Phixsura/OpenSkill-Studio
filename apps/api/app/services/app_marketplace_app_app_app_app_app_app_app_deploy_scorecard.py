"""Deployment scorecard — rate deployment quality across dimensions."""
from __future__ import annotations


def score_deployment(deployment: dict) -> dict:
    dimensions = {
        "tests": 25 if deployment.get("all_tests_passed") else 0,
        "security": 20 if deployment.get("security_clean") else 0,
        "canary": 15 if deployment.get("canary_passed") else 0,
        "rollback": 10 if deployment.get("rollback_tested") else 0,
        "monitoring": 15 if deployment.get("monitoring_ready") else 0,
        "review": 15 if deployment.get("peer_reviewed") else 0,
    }
    score = sum(dimensions.values())
    grade = "A" if score >= 90 else ("B" if score >= 70 else ("C" if score >= 50 else "F"))
    return {"score": score, "grade": grade, "dimensions": dimensions,
            "version": deployment.get("version", ""),
            "deploy_ready": score >= 70}
