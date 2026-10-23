"""Platform invite system — team invitations with RSVP tracking."""
from __future__ import annotations
import secrets
import time


class InviteSystem:
    def __init__(self):
        self._invites: dict[str, dict] = {}

    def send(self, *, email: str, org_id: str, role: str = "member",
              invited_by: str = "", expires_hours: int = 72) -> dict:
        code = secrets.token_urlsafe(16)
        self._invites[code] = {
            "code": code, "email": email, "org_id": org_id,
            "role": role, "invited_by": invited_by,
            "status": "pending", "sent_at": time.time(),
            "expires_in": expires_hours * 3600,
        }
        return {"code": code, "email": email, "role": role, "status": "pending"}

    def accept(self, code: str) -> dict:
        inv = self._invites.get(code)
        if not inv:
            return {"error": "Invite not found"}
        if inv["status"] != "pending":
            return {"error": f"Invite already {inv['status']}"}
        inv["status"] = "accepted"
        return {"accepted": True, "org_id": inv["org_id"], "role": inv["role"]}

    def decline(self, code: str) -> dict:
        inv = self._invites.get(code)
        if not inv:
            return {"error": "Invite not found"}
        inv["status"] = "declined"
        return {"declined": True}

    def pending_for_org(self, org_id: str) -> list[dict]:
        return [{"email": i["email"], "role": i["role"], "status": i["status"]}
                for i in self._invites.values()
                if i["org_id"] == org_id and i["status"] == "pending"]
