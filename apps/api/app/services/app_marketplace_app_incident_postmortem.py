"""Incident postmortem — structured postmortem reports for resolved incidents."""

from datetime import datetime, timezone


def create_postmortem(*, incident_id: str, title: str, summary: str, root_cause: str,
                        timeline: list[dict], action_items: list[dict]) -> dict:
    return {
        "incident_id": incident_id, "title": title, "summary": summary,
        "root_cause": root_cause, "timeline": timeline,
        "action_items": action_items, "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def track_action_items(*, items: list[dict]) -> dict:
    completed = sum(1 for i in items if i.get("status") == "completed")
    return {"total": len(items), "completed": completed, "pending": len(items) - completed,
            "completion_pct": round(completed / max(len(items), 1) * 100)}
