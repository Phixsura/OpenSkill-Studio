"""Platform command center — unified operational overview."""
from __future__ import annotations


def build_command_center(data: dict) -> dict:
    services = data.get("services", {})
    deploys = data.get("deployments", {})
    alerts = data.get("alerts", {})
    score = round(
        services.get("healthy_pct", 100) * 0.4 +
        (100 - alerts.get("critical", 0) * 10) * 0.3 +
        deploys.get("success_rate", 100) * 0.3, 1)
    status = "green" if score >= 90 else "yellow" if score >= 70 else "red"
    return {"score": min(score, 100), "status": status,
            "services": services, "deployments": deploys, "alerts": alerts,
            "action_items": _get_actions(services, deploys, alerts)}


def _get_actions(services: dict, deploys: dict, alerts: dict) -> list[str]:
    actions = []
    if services.get("unhealthy", 0) > 0:
        actions.append(f"Investigate {services['unhealthy']} unhealthy services")
    if alerts.get("critical", 0) > 0:
        actions.append(f"Resolve {alerts['critical']} critical alerts")
    if deploys.get("failed", 0) > 0:
        actions.append(f"Check {deploys['failed']} failed deployments")
    return actions
