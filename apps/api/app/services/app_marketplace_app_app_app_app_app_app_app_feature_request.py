"""Feature request tracker — collect, vote, and prioritize feature requests."""
from __future__ import annotations
import html


class FeatureRequestTracker:
    def __init__(self):
        self._requests: list[dict] = []

    def submit(self, *, title: str, description: str, author: str,
                category: str = "general") -> dict:
        rid = len(self._requests) + 1
        req = {"id": rid, "title": html.escape(title),
               "description": html.escape(description[:1000]),
               "author": author, "category": category,
               "votes": 0, "status": "open", "voters": set()}
        self._requests.append(req)
        return {"id": rid, "title": html.escape(title), "status": "open"}

    def vote(self, request_id: int, user_id: str) -> dict:
        req = next((r for r in self._requests if r["id"] == request_id), None)
        if not req:
            return {"error": "Request not found"}
        if user_id in req["voters"]:
            return {"error": "Already voted"}
        req["voters"].add(user_id)
        req["votes"] += 1
        return {"id": request_id, "votes": req["votes"]}

    def top_requests(self, *, limit: int = 10, status: str | None = None) -> list[dict]:
        filtered = self._requests
        if status:
            filtered = [r for r in filtered if r["status"] == status]
        ranked = sorted(filtered, key=lambda r: -r["votes"])[:limit]
        return [{"id": r["id"], "title": r["title"], "votes": r["votes"],
                 "status": r["status"], "category": r["category"]} for r in ranked]

    def stats(self) -> dict:
        total = len(self._requests)
        open_count = sum(1 for r in self._requests if r["status"] == "open")
        total_votes = sum(r["votes"] for r in self._requests)
        return {"total": total, "open": open_count, "total_votes": total_votes}
