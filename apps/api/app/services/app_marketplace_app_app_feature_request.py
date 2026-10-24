"""Feature request — user feature voting and tracking."""

import html
import secrets
from datetime import datetime, timezone

STATUSES = ["open", "under_review", "planned", "in_progress", "completed", "declined"]


def create_feature_request(*, title: str, description: str, author: str,
                              category: str = "general") -> dict:
    return {"id": f"feat_{secrets.token_hex(6)}",
            "title": html.escape(title), "description": html.escape(description),
            "author": html.escape(author), "category": category,
            "status": "open", "votes": 0,
            "created_at": datetime.now(timezone.utc).isoformat()}


def build_feature_board(*, requests: list[dict]) -> dict:
    by_status: dict[str, list] = {}
    for r in requests:
        s = r.get("status", "open")
        by_status.setdefault(s, []).append(r)
    for status_list in by_status.values():
        status_list.sort(key=lambda x: x.get("votes", 0), reverse=True)
    total_votes = sum(r.get("votes", 0) for r in requests)
    return {"columns": by_status, "total": len(requests),
            "total_votes": total_votes,
            "status_counts": {s: len(items) for s, items in by_status.items()}}
