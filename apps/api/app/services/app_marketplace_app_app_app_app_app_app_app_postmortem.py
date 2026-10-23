"""Incident postmortem — create and track postmortem reports."""
from __future__ import annotations
import html
import time


def create_postmortem(incident_id: str, title: str, severity: str,
                       timeline: list[dict], root_cause: str,
                       action_items: list[dict]) -> dict:
    completed = sum(1 for a in action_items if a.get("done", False))
    return {"incident_id": incident_id, "title": html.escape(title),
            "severity": severity, "timeline": timeline,
            "root_cause": html.escape(root_cause),
            "action_items": action_items, "action_count": len(action_items),
            "completed_actions": completed,
            "progress_pct": round(completed / max(len(action_items), 1) * 100),
            "created_at": time.time()}


def postmortem_stats(postmortems: list[dict]) -> dict:
    total_actions = sum(p["action_count"] for p in postmortems)
    completed = sum(p["completed_actions"] for p in postmortems)
    by_sev: dict[str, int] = {}
    for p in postmortems:
        by_sev[p["severity"]] = by_sev.get(p["severity"], 0) + 1
    return {"total": len(postmortems), "total_actions": total_actions,
            "completed_actions": completed, "by_severity": by_sev,
            "action_completion_pct": round(completed / max(total_actions, 1) * 100)}
