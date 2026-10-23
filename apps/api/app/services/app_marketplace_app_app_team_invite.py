"""Team invite — team member invitation with role assignment."""

import html
import secrets
import re
from datetime import datetime, timezone, timedelta

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
ROLES = {"viewer", "editor", "admin"}


def send_invite(*, email: str, role: str, org_name: str, inviter: str) -> dict:
    if not EMAIL_RE.match(email):
        return {"error": "Invalid email"}
    if role not in ROLES:
        return {"error": f"Invalid role. Must be: {', '.join(sorted(ROLES))}"}
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    return {
        "invite_id": f"inv_{secrets.token_hex(6)}",
        "email": email, "role": role,
        "org_name": html.escape(org_name),
        "inviter": html.escape(inviter),
        "token": token, "status": "pending",
        "sent_at": now.isoformat(),
        "expires_at": (now + timedelta(days=7)).isoformat(),
    }


def build_pending_invites(*, invites: list[dict]) -> dict:
    pending = [i for i in invites if i.get("status") == "pending"]
    accepted = [i for i in invites if i.get("status") == "accepted"]
    return {"pending": pending, "accepted": accepted,
            "pending_count": len(pending), "accepted_count": len(accepted),
            "total": len(invites)}
