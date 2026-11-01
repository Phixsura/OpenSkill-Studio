"""Invite system — manage app team invitations."""

import secrets
from datetime import datetime, timedelta


def create_invite(*, app_id: str, email: str, role: str = "developer",
                    invited_by: str, expires_hours: int = 72) -> dict:
    valid_roles = {"developer", "viewer", "admin"}
    if role not in valid_roles:
        return {"error": f"Invalid role. Valid: {', '.join(sorted(valid_roles))}"}
    if "@" not in email or "." not in email.split("@")[-1]:
        return {"error": "Invalid email address"}
    token = secrets.token_urlsafe(24)
    return {
        "invite_id": f"inv_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "email": email,
        "role": role,
        "invited_by": invited_by,
        "token": token,
        "invite_url": f"https://marketplace.openskill.dev/invite/{token}",
        "expires_at": (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat(),
        "status": "pending",
    }


def accept_invite(*, token: str, user_id: str) -> dict:
    if len(token) < 10:
        return {"success": False, "error": "Invalid token"}
    return {"success": True, "user_id": user_id, "status": "accepted",
            "message": "Welcome to the team!"}


def list_pending_invites(*, app_id: str) -> dict:
    return {
        "app_id": app_id,
        "invites": [
            {"invite_id": "inv_1", "email": "bob@example.com", "role": "developer", "status": "pending"},
            {"invite_id": "inv_2", "email": "carol@example.com", "role": "viewer", "status": "pending"},
        ],
        "total": 2,
    }
