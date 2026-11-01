"""Fleet Code Review v9 — track PR review velocity and quality."""
from __future__ import annotations
def fleet_code_review_v9(reviews: list[dict]) -> dict:
    approved = [r for r in reviews if r.get("status") == "approved"]
    changes_req = [r for r in reviews if r.get("status") == "changes_requested"]
    avg_time = sum(r.get("review_hours", 0) for r in reviews) / len(reviews) if reviews else 0
    return {"total": len(reviews), "approved": len(approved), "changes_requested": len(changes_req),
            "avg_review_hours": round(avg_time, 1), "healthy": avg_time < 24}
