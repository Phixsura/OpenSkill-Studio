"""Contact form — developer support contact form."""

import html
import re
import secrets
from datetime import datetime, timezone

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
TOPICS = ["general", "billing", "technical", "partnership", "bug_report", "feature_request"]


def submit_contact(*, name: str, email: str, topic: str, message: str) -> dict:
    errors = []
    if not name.strip():
        errors.append("Name is required")
    if not EMAIL_RE.match(email):
        errors.append("Valid email is required")
    if topic not in TOPICS:
        errors.append(f"Topic must be: {', '.join(TOPICS)}")
    if len(message.strip()) < 20:
        errors.append("Message must be at least 20 characters")
    if errors:
        return {"submitted": False, "errors": errors}
    return {
        "submitted": True,
        "ticket_id": f"CTK-{secrets.token_hex(4).upper()}",
        "name": html.escape(name), "email": email, "topic": topic,
        "message": html.escape(message[:2000]),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "response_time": "Within 24 hours",
    }
