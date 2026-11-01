"""Platform operations center — unified ops view for the entire platform."""
from __future__ import annotations


def build_ops_center(data: dict) -> dict:
    services = data.get("services", {})
    infra = data.get("infrastructure", {})
    security = data.get("security", {})
    deploys = data.get("deployments", {})
    
    service_score = services.get("healthy_pct", 100)
    infra_score = infra.get("uptime_pct", 100)
    security_score = security.get("compliance_pct", 100)
    deploy_score = deploys.get("success_rate", 100)
    
    overall = round((service_score * 0.3 + infra_score * 0.3 + 
                      security_score * 0.2 + deploy_score * 0.2), 1)
    status = "green" if overall >= 95 else "yellow" if overall >= 80 else "red"
    
    return {"overall_score": overall, "status": status,
            "dimensions": {"services": service_score, "infrastructure": infra_score,
                           "security": security_score, "deployments": deploy_score},
            "action_items": _get_action_items(data)}


def _get_action_items(data: dict) -> list[str]:
    items = []
    if data.get("services", {}).get("unhealthy", 0) > 0:
        items.append(f"{data['services']['unhealthy']} unhealthy services")
    if data.get("security", {}).get("violations", 0) > 0:
        items.append(f"{data['security']['violations']} security violations")
    if data.get("deployments", {}).get("failed", 0) > 0:
        items.append(f"{data['deployments']['failed']} failed deployments")
    return items
