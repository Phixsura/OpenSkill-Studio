"""Change risk assessment — evaluate risk of proposed changes."""
from __future__ import annotations


RISK_FACTORS = {
    "files_changed": {"weight": 0.2, "high_threshold": 50},
    "services_affected": {"weight": 0.25, "high_threshold": 5},
    "database_migration": {"weight": 0.2, "high_threshold": 1},
    "config_changes": {"weight": 0.15, "high_threshold": 10},
    "rollback_complexity": {"weight": 0.2, "high_threshold": 3},
}


def assess_change_risk(change: dict) -> dict:
    risk_score = 0
    factors = []
    for factor, config in RISK_FACTORS.items():
        value = change.get(factor, 0)
        normalized = min(value / max(config["high_threshold"], 1), 1.0)
        weighted = round(normalized * config["weight"] * 100, 1)
        risk_score += weighted
        factors.append({"factor": factor, "value": value,
                         "threshold": config["high_threshold"],
                         "risk_contribution": weighted, "high": value >= config["high_threshold"]})
    risk_score = round(min(risk_score, 100))
    level = "critical" if risk_score >= 80 else "high" if risk_score >= 60 else "medium" if risk_score >= 30 else "low"
    return {"risk_score": risk_score, "risk_level": level, "factors": factors,
            "deploy_caution": level in ("high", "critical")}
