"""App deploy history — deployment history with rollback options."""

import html
from datetime import datetime, timezone


def build_deploy_history(*, deploys: list[dict], current_version: str = "") -> dict:
    items = []
    for d in sorted(deploys, key=lambda x: x.get("deployed_at", ""), reverse=True):
        items.append({
            "id": d.get("id", ""),
            "version": d.get("version", ""),
            "environment": d.get("environment", "production"),
            "status": d.get("status", "success"),
            "deployed_at": d.get("deployed_at", ""),
            "deployer": html.escape(d.get("deployer", "")),
            "commit": d.get("commit", "")[:8],
            "duration_s": d.get("duration_s", 0),
            "is_current": d.get("version") == current_version,
            "can_rollback": d.get("version") != current_version and d.get("status") == "success",
        })
    success_rate = round(sum(1 for d in items if d["status"] == "success") / max(len(items), 1) * 100, 1)
    return {"deploys": items[:20], "total": len(items), "current_version": current_version,
            "success_rate": success_rate,
            "avg_duration_s": round(sum(d["duration_s"] for d in items) / max(len(items), 1))}
