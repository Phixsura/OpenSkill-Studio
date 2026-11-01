"""App review queue — manage the app review pipeline for marketplace publishing."""
from __future__ import annotations
import html

REVIEW_STAGES = ["submitted", "automated_scan", "manual_review", "approved", "rejected"]


def build_review_queue(submissions: list[dict]) -> dict:
    by_stage: dict[str, list[dict]] = {s: [] for s in REVIEW_STAGES}
    for sub in submissions:
        stage = sub.get("stage", "submitted")
        if stage in by_stage:
            by_stage[stage].append({
                "app_name": html.escape(sub.get("app_name", "")),
                "developer": html.escape(sub.get("developer", "")),
                "submitted_at": sub.get("submitted_at", ""),
                "stage": stage,
            })
    pending = sum(len(v) for k, v in by_stage.items() if k not in ("approved", "rejected"))
    return {"stages": by_stage, "pending_count": pending,
            "total": len(submissions),
            "approved_count": len(by_stage["approved"]),
            "rejected_count": len(by_stage["rejected"])}
