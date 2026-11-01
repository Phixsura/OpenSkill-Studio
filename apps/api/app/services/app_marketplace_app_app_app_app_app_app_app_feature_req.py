"""Feature request tracker — collect and prioritize feature requests."""
from __future__ import annotations
import html
import time

_requests: list[dict] = []


def submit_request(title: str, description: str, submitter: str, category: str = "general") -> dict:
    req = {"id": len(_requests) + 1, "title": html.escape(title),
           "description": html.escape(description), "submitter": submitter,
           "category": category, "votes": 1, "status": "open",
           "created_at": time.time(), "voters": {submitter}}
    _requests.append(req)
    return {"id": req["id"], "title": req["title"], "status": "open"}


def vote(request_id: int, user_id: str) -> dict:
    for r in _requests:
        if r["id"] == request_id:
            if user_id in r["voters"]:
                return {"voted": False, "error": "already_voted"}
            r["voters"].add(user_id)
            r["votes"] += 1
            return {"voted": True, "votes": r["votes"]}
    return {"voted": False, "error": "not_found"}


def top_requests(limit: int = 10) -> list[dict]:
    open_reqs = [r for r in _requests if r["status"] == "open"]
    return sorted(open_reqs, key=lambda r: -r["votes"])[:limit]


def request_stats() -> dict:
    open_count = sum(1 for r in _requests if r["status"] == "open")
    by_cat: dict[str, int] = {}
    for r in _requests:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    return {"total": len(_requests), "open": open_count, "by_category": by_cat}


def clear_requests() -> None:
    _requests.clear()
