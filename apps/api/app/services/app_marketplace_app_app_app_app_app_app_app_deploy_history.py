"""Deployment history — track all deployments for an app."""
from __future__ import annotations
import html


def build_deploy_history(deploys: list[dict]) -> dict:
    items = []
    success_count = 0
    for d in deploys:
        status = d.get("status", "success")
        if status == "success":
            success_count += 1
        items.append({
            "version": d.get("version", ""),
            "environment": d.get("environment", "production"),
            "status": status,
            "deployer": html.escape(d.get("deployer", "")),
            "timestamp": d.get("timestamp", ""),
            "duration_sec": d.get("duration_sec", 0),
        })
    total = len(items)
    success_rate = round(success_count / max(total, 1) * 100)
    return {"deploys": items, "total": total, "success_count": success_count,
            "failure_count": total - success_count,
            "success_rate": success_rate, "success_display": f"{success_rate}%"}
