"""Invite link manager — create, validate, and expire invite links."""
from __future__ import annotations
import secrets
import time


class InviteLinkManager:
    def __init__(self):
        self._links: dict[str, dict] = {}

    def create(self, *, org_id: str, role: str = "member",
               max_uses: int = 0, expires_in: int = 604800) -> dict:
        code = secrets.token_urlsafe(16)
        now = time.time()
        self._links[code] = {
            "org_id": org_id, "role": role, "max_uses": max_uses,
            "uses": 0, "created": now, "expires": now + expires_in,
        }
        return {"code": code, "url": f"https://app.openskill.io/invite/{code}",
                "role": role, "max_uses": max_uses or "unlimited",
                "expires_in": expires_in}

    def validate(self, code: str, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        link = self._links.get(code)
        if not link:
            return {"valid": False, "reason": "not_found"}
        if ts > link["expires"]:
            return {"valid": False, "reason": "expired"}
        if link["max_uses"] > 0 and link["uses"] >= link["max_uses"]:
            return {"valid": False, "reason": "max_uses_reached"}
        return {"valid": True, "org_id": link["org_id"], "role": link["role"]}

    def redeem(self, code: str) -> dict:
        v = self.validate(code)
        if not v["valid"]:
            return v
        self._links[code]["uses"] += 1
        return {"redeemed": True, "org_id": v["org_id"], "role": v["role"],
                "uses": self._links[code]["uses"]}

    def revoke(self, code: str) -> dict:
        if code not in self._links:
            return {"status": "not_found"}
        self._links[code]["expires"] = 0
        return {"status": "revoked", "code": code}
