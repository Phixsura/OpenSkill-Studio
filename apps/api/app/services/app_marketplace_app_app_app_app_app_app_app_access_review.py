"""Access reviewer — periodic access reviews for compliance."""
from __future__ import annotations
import time


def create_review(reviewer: str, users: list[dict]) -> dict:
    items = []
    for u in users:
        items.append({"user_id": u["id"], "role": u.get("role", "viewer"),
                       "last_active": u.get("last_active_days", 0),
                       "decision": "pending"})
    return {"reviewer": reviewer, "items": items, "total": len(items),
            "reviewed": 0, "created_at": time.time()}


def decide(review: dict, user_id: str, decision: str) -> dict:
    valid = {"approve", "revoke", "downgrade"}
    if decision not in valid:
        return {"decided": False, "error": "invalid_decision"}
    for item in review["items"]:
        if item["user_id"] == user_id:
            item["decision"] = decision
            review["reviewed"] += 1
            return {"decided": True, "user_id": user_id, "decision": decision,
                    "progress": round(review["reviewed"] / review["total"] * 100)}
    return {"decided": False, "error": "user_not_found"}


def review_summary(review: dict) -> dict:
    by_decision: dict[str, int] = {}
    for item in review["items"]:
        by_decision[item["decision"]] = by_decision.get(item["decision"], 0) + 1
    return {"total": review["total"], "reviewed": review["reviewed"],
            "by_decision": by_decision,
            "complete": review["reviewed"] == review["total"]}
