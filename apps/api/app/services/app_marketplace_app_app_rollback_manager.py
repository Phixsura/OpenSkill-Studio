"""Rollback manager — deployment rollback with version history."""

import html
from datetime import datetime, timezone


def build_rollback_options(*, deployments: list[dict], current_version: str) -> dict:
    options = []
    for d in deployments:
        ver = d.get("version", "")
        if ver == current_version:
            continue
        options.append({
            "version": ver,
            "deployed_at": d.get("deployed_at", ""),
            "commit": d.get("commit", "")[:8],
            "author": html.escape(d.get("author", "")),
            "status": d.get("status", "success"),
        })
    options.sort(key=lambda x: x["deployed_at"], reverse=True)
    return {"current": current_version, "options": options[:10],
            "available": len(options), "can_rollback": len(options) > 0}


def execute_rollback(*, target_version: str, reason: str = "") -> dict:
    return {"action": "rollback", "target_version": target_version,
            "reason": html.escape(reason),
            "initiated_at": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress"}
