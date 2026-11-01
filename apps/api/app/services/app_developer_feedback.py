"""Developer feedback — collect and manage developer feedback."""

from datetime import UTC, datetime
from collections import defaultdict

_feedback: list[dict] = []
FEEDBACK_TYPES = ["bug", "feature_request", "question", "praise", "other"]


def submit_feedback(*, developer_id: str, feedback_type: str, message: str, page: str = "") -> dict | None:
    if feedback_type not in FEEDBACK_TYPES:
        return None
    entry = {"developer_id": developer_id, "type": feedback_type, "message": message,
             "page": page, "status": "open", "created_at": datetime.now(UTC).isoformat()}
    _feedback.append(entry)
    return entry


def get_feedback_stats() -> dict:
    by_type = defaultdict(int)
    for f in _feedback:
        by_type[f["type"]] += 1
    return {"total": len(_feedback), "by_type": dict(by_type), "open": sum(1 for f in _feedback if f["status"] == "open")}
