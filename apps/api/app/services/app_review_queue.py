"""App review queue — manage review queue for platform admins."""

from collections import defaultdict
from datetime import UTC, datetime

_queue: list[dict] = []


def submit_for_review(*, app_id: str, version_id: str, submitted_by: str) -> dict:
    entry = {
        "app_id": app_id, "version_id": version_id, "submitted_by": submitted_by,
        "status": "pending", "submitted_at": datetime.now(UTC).isoformat(),
        "reviewer_id": None, "reviewed_at": None,
    }
    _queue.append(entry)
    return entry


def get_pending_reviews() -> list[dict]:
    return [r for r in _queue if r["status"] == "pending"]


def assign_reviewer(app_id: str, reviewer_id: str) -> bool:
    for r in _queue:
        if r["app_id"] == app_id and r["status"] == "pending":
            r["reviewer_id"] = reviewer_id
            r["status"] = "in_review"
            return True
    return False


def complete_review(app_id: str, *, decision: str, notes: str = "") -> bool:
    for r in _queue:
        if r["app_id"] == app_id and r["status"] == "in_review":
            r["status"] = decision  # "approved" or "rejected"
            r["reviewed_at"] = datetime.now(UTC).isoformat()
            r["notes"] = notes
            return True
    return False


def get_queue_stats() -> dict:
    statuses = defaultdict(int)
    for r in _queue:
        statuses[r["status"]] += 1
    return {"total": len(_queue), "by_status": dict(statuses)}
