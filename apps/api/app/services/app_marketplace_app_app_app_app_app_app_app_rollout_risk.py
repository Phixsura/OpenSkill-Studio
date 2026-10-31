"""Rollout risk assessment — evaluate risk before rolling out changes."""
from __future__ import annotations


def assess_rollout_risk(change: dict) -> dict:
    risk_factors = []
    score = 0
    if change.get("lines_changed", 0) > 500:
        risk_factors.append("large_change")
        score += 20
    if change.get("services_affected", 0) > 3:
        risk_factors.append("multi_service")
        score += 25
    if change.get("database_migration", False):
        risk_factors.append("database_migration")
        score += 30
    if change.get("config_change", False):
        risk_factors.append("config_change")
        score += 10
    if not change.get("has_rollback_plan", False):
        risk_factors.append("no_rollback_plan")
        score += 15
    level = "critical" if score >= 60 else "high" if score >= 40 else "medium" if score >= 20 else "low"
    return {"risk_score": min(score, 100), "risk_level": level,
            "risk_factors": risk_factors, "factor_count": len(risk_factors),
            "recommend_canary": score >= 30}
