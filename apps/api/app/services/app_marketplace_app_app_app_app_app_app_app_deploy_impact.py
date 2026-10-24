"""Deployment impact analyzer — analyze the impact of a deployment on the system."""
from __future__ import annotations


def analyze_impact(deployment: dict, system_state: dict) -> dict:
    services_affected = deployment.get("services", [])
    total_services = system_state.get("total_services", 0)
    impact_pct = round(len(services_affected) / max(total_services, 1) * 100, 1)
    users_affected = 0
    for svc in services_affected:
        users_affected += system_state.get("service_users", {}).get(svc, 0)
    risk_factors = []
    if deployment.get("has_db_migration"):
        risk_factors.append("database_migration")
    if deployment.get("breaking_changes"):
        risk_factors.append("breaking_api_changes")
    if len(services_affected) > 3:
        risk_factors.append("wide_blast_radius")
    if deployment.get("env") == "production":
        risk_factors.append("production_deployment")
    risk = "high" if len(risk_factors) >= 3 else ("medium" if len(risk_factors) >= 1 else "low")
    return {"services_affected": services_affected, "impact_pct": impact_pct,
            "users_affected": users_affected, "risk": risk,
            "risk_factors": risk_factors, "env": deployment.get("env", "")}


def should_require_approval(impact: dict) -> dict:
    require = impact["risk"] in ("high", "medium") or impact["impact_pct"] > 20
    return {"require_approval": require, "risk": impact["risk"],
            "reason": "high_impact" if require else "low_impact"}
