"""Change management tracker — track and approve infrastructure changes."""
from __future__ import annotations
import time


class ChangeTracker:
    def __init__(self):
        self._changes: dict[str, dict] = {}

    def create(self, change_id: str, title: str, risk: str, requester: str) -> dict:
        self._changes[change_id] = {
            "id": change_id, "title": title, "risk": risk,
            "requester": requester, "status": "draft",
            "approvals": [], "created_at": time.time()}
        return self._changes[change_id]

    def submit(self, change_id: str) -> dict:
        c = self._changes[change_id]
        c["status"] = "pending_review"
        return {"id": change_id, "status": c["status"]}

    def approve(self, change_id: str, approver: str) -> dict:
        c = self._changes[change_id]
        c["approvals"].append(approver)
        required = 2 if c["risk"] == "high" else 1
        if len(c["approvals"]) >= required:
            c["status"] = "approved"
        return {"id": change_id, "status": c["status"],
                "approvals": len(c["approvals"]), "required": required}

    def implement(self, change_id: str) -> dict:
        c = self._changes[change_id]
        if c["status"] != "approved":
            return {"id": change_id, "success": False, "reason": "not_approved"}
        c["status"] = "implemented"
        return {"id": change_id, "success": True, "status": "implemented"}

    def stats(self) -> dict:
        by_status = {}
        for c in self._changes.values():
            by_status[c["status"]] = by_status.get(c["status"], 0) + 1
        return {"total": len(self._changes), "by_status": by_status}
