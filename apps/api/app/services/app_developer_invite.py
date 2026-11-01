"""Developer invite — invite collaborators to a developer account."""

import secrets
from datetime import UTC, datetime, timedelta

_invites: dict[str, dict] = {}


def create_invite(*, developer_id: str, email: str, role: str = "member") -> dict:
    code = secrets.token_urlsafe(32)
    invite = {
        "code": code, "developer_id": developer_id, "email": email, "role": role,
        "status": "pending", "created_at": datetime.now(UTC).isoformat(),
        "expires_at": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
    }
    _invites[code] = invite
    return invite


def accept_invite(code: str, *, user_id: str) -> dict | None:
    invite = _invites.get(code)
    if not invite or invite["status"] != "pending":
        return None
    if datetime.fromisoformat(invite["expires_at"]) < datetime.now(UTC):
        invite["status"] = "expired"
        return None
    invite["status"] = "accepted"
    invite["accepted_by"] = user_id
    return invite


def list_pending_invites(developer_id: str) -> list[dict]:
    return [i for i in _invites.values() if i["developer_id"] == developer_id and i["status"] == "pending"]


def revoke_invite(code: str) -> bool:
    invite = _invites.get(code)
    if invite and invite["status"] == "pending":
        invite["status"] = "revoked"
        return True
    return False
