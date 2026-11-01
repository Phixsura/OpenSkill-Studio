"""Fleet AI Code Review — track automated code review and suggestions."""
from __future__ import annotations
def fleet_ai_code_review(reviewers: list[dict]) -> dict:
    active = [r for r in reviewers if r.get("active", True)]
    prs_reviewed_24h = sum(r.get("prs_24h", 0) for r in reviewers)
    suggestions = sum(r.get("suggestions", 0) for r in reviewers)
    accepted = sum(r.get("accepted", 0) for r in reviewers)
    accept_rate = round(accepted / max(suggestions, 1) * 100, 1)
    return {"reviewers": len(reviewers), "active": len(active), "prs_24h": prs_reviewed_24h,
            "suggestions": suggestions, "accepted": accepted, "accept_rate": accept_rate}
