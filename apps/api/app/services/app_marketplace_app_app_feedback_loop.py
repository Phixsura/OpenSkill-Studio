"""Feedback loop — close-loop feedback from users to developers."""

import secrets
from datetime import datetime


FEEDBACK_STATUSES = {"open", "acknowledged", "planned", "in_progress", "shipped", "declined"}


def submit_feedback(*, user_id: str, app_id: str, category: str,
                      title: str, description: str) -> dict:
    valid_cats = {"bug", "feature", "improvement", "question"}
    if category not in valid_cats:
        return {"error": f"Invalid category. Valid: {', '.join(sorted(valid_cats))}"}
    return {
        "feedback_id": f"fb_{secrets.token_urlsafe(8)}",
        "user_id": user_id,
        "app_id": app_id,
        "category": category,
        "title": title,
        "description": description,
        "status": "open",
        "votes": 1,
        "created_at": datetime.utcnow().isoformat(),
    }


def update_status(*, feedback_id: str, status: str, developer_note: str | None = None) -> dict:
    if status not in FEEDBACK_STATUSES:
        return {"error": f"Invalid status. Valid: {', '.join(sorted(FEEDBACK_STATUSES))}"}
    return {"feedback_id": feedback_id, "status": status,
            "developer_note": developer_note, "updated": True}


def get_feedback_board(*, items: list[dict]) -> dict:
    by_status: dict[str, list] = {}
    for item in items:
        s = item.get("status", "open")
        by_status.setdefault(s, []).append(item)
    for k in by_status:
        by_status[k].sort(key=lambda x: x.get("votes", 0), reverse=True)
    return {"columns": by_status, "total": len(items),
            "open_count": len(by_status.get("open", []))}
