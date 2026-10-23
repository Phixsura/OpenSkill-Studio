"""App transfer — ownership transfer between organizations."""

import html
import secrets
from datetime import datetime, timezone, timedelta


def initiate_transfer(*, app_id: str, from_org: str, to_org: str,
                        initiated_by: str) -> dict:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    return {
        "transfer_id": f"xfr_{secrets.token_hex(8)}",
        "app_id": app_id, "from_org": html.escape(from_org),
        "to_org": html.escape(to_org), "initiated_by": html.escape(initiated_by),
        "token": token, "status": "pending_acceptance",
        "initiated_at": now.isoformat(),
        "expires_at": (now + timedelta(days=7)).isoformat(),
    }


def build_transfer_status(*, transfers: list[dict]) -> dict:
    pending = [t for t in transfers if t.get("status") == "pending_acceptance"]
    completed = [t for t in transfers if t.get("status") == "completed"]
    return {"transfers": transfers, "total": len(transfers),
            "pending": len(pending), "completed": len(completed),
            "has_pending": len(pending) > 0}
