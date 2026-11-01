"""Contact form handler — validate and process contact form submissions."""
from __future__ import annotations
import html
import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
TOPICS = ["general", "support", "sales", "partnerships", "bug_report", "feature_request"]


def validate_contact(*, name: str, email: str, topic: str, message: str) -> dict:
    errors = []
    if len(name.strip()) < 2:
        errors.append({"field": "name", "error": "Name must be at least 2 characters"})
    if not EMAIL_RE.match(email):
        errors.append({"field": "email", "error": "Invalid email address"})
    if topic not in TOPICS:
        errors.append({"field": "topic", "error": f"Must be one of: {', '.join(TOPICS)}"})
    if len(message.strip()) < 20:
        errors.append({"field": "message", "error": "Message must be at least 20 characters"})
    return {"valid": len(errors) == 0, "errors": errors}


def process_contact(*, name: str, email: str, topic: str, message: str) -> dict:
    v = validate_contact(name=name, email=email, topic=topic, message=message)
    if not v["valid"]:
        return {"submitted": False, "validation": v}
    return {"submitted": True, "safe_name": html.escape(name),
            "safe_email": email, "topic": topic,
            "safe_message": html.escape(message[:5000]),
            "confirmation": f"Thanks {html.escape(name)}! We'll respond within 24 hours."}
