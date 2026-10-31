"""Account deletion — GDPR-compliant account deletion with data export."""

import html
import secrets
from datetime import datetime, timezone, timedelta

GRACE_PERIOD_DAYS = 30
DATA_CATEGORIES = ["profile", "apps", "analytics", "webhooks", "api_keys", "billing"]


def request_deletion(*, user_id: str, reason: str = "") -> dict:
    now = datetime.now(timezone.utc)
    deletion_date = now + timedelta(days=GRACE_PERIOD_DAYS)
    return {
        "request_id": f"del_{secrets.token_hex(8)}",
        "user_id": user_id,
        "reason": html.escape(reason),
        "status": "pending",
        "requested_at": now.isoformat(),
        "scheduled_deletion": deletion_date.isoformat(),
        "grace_period_days": GRACE_PERIOD_DAYS,
        "data_to_delete": DATA_CATEGORIES,
        "can_cancel": True,
    }


def build_deletion_summary(*, data_counts: dict[str, int]) -> dict:
    items = []
    total = 0
    for cat in DATA_CATEGORIES:
        count = data_counts.get(cat, 0)
        total += count
        items.append({"category": cat, "count": count, "label": cat.replace("_", " ").title()})
    return {"items": items, "total_records": total,
            "categories": len(DATA_CATEGORIES)}
