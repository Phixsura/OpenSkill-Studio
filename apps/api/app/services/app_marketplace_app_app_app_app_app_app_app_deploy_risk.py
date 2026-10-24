"""Deployment risk scorer — score deployment risk from multiple factors."""
from __future__ import annotations


def score_deployment_risk(deployment: dict) -> dict:
    score = 0
    factors = []
    if deployment.get("env") == "production":
        score += 15; factors.append("production")
    if deployment.get("has_migration"):
        score += 20; factors.append("db_migration")
    if deployment.get("breaking_changes"):
        score += 25; factors.append("breaking_changes")
    services = deployment.get("services_affected", 1)
    if services > 5:
        score += 20; factors.append("wide_blast_radius")
    elif services > 1:
        score += 10; factors.append("multi_service")
    if deployment.get("peak_hours"):
        score += 15; factors.append("peak_hours")
    if not deployment.get("rollback_plan"):
        score += 10; factors.append("no_rollback_plan")
    score = min(score, 100)
    level = "critical" if score >= 70 else ("high" if score >= 40 else ("medium" if score >= 20 else "low"))
    return {"score": score, "level": level, "factors": factors}
