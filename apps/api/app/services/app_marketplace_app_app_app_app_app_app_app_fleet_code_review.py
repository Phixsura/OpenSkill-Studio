"""Fleet code review — track review turnaround and coverage."""
from __future__ import annotations
def fleet_code_review(prs: list[dict]) -> dict:
    reviewed = [p for p in prs if p.get("reviewed", False)]
    avg_hours = round(sum(p.get("review_hours", 0) for p in reviewed) / max(len(reviewed), 1), 1)
    return {"total_prs": len(prs), "reviewed": len(reviewed),
            "unreviewed": len(prs) - len(reviewed), "avg_review_hours": avg_hours,
            "fast": avg_hours <= 24}
