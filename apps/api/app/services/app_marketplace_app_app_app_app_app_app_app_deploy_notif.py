"""Deployment notification engine — notify stakeholders about deployments."""
from __future__ import annotations
import html


CHANNELS = {"slack", "email", "pagerduty", "teams", "webhook"}


def create_notification(deployment_id: str, version: str, environment: str,
                          deployer: str, status: str, channels: list[str]) -> dict:
    invalid = [c for c in channels if c not in CHANNELS]
    if invalid:
        return {"sent": False, "error": f"invalid channels: {invalid}"}
    recipients = []
    for ch in channels:
        recipients.append({"channel": ch, "status": "delivered"})
    return {"sent": True, "deployment_id": deployment_id, "version": version,
            "environment": environment, "deployer": html.escape(deployer),
            "deploy_status": status, "recipients": recipients,
            "channels_notified": len(recipients)}


def notification_summary(notifications: list[dict]) -> dict:
    total = len(notifications)
    by_env: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for n in notifications:
        by_env[n.get("environment", "")] = by_env.get(n.get("environment", ""), 0) + 1
        by_status[n.get("deploy_status", "")] = by_status.get(n.get("deploy_status", ""), 0) + 1
    return {"total": total, "by_environment": by_env, "by_status": by_status}
