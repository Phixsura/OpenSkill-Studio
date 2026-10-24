"""App submission flow — submit apps for marketplace review with validation."""
from __future__ import annotations
import html

REQUIRED_FIELDS = ["name", "description", "category", "icon_url", "developer_name"]
OPTIONAL_FIELDS = ["website", "privacy_url", "terms_url", "screenshots"]


def validate_submission(app: dict) -> dict:
    errors = []
    for field in REQUIRED_FIELDS:
        if not app.get(field):
            errors.append({"field": field, "error": f"{field} is required"})
    name = app.get("name", "")
    if name and (len(name) < 3 or len(name) > 50):
        errors.append({"field": "name", "error": "Name must be 3-50 characters"})
    desc = app.get("description", "")
    if desc and len(desc) < 20:
        errors.append({"field": "description", "error": "Description must be at least 20 characters"})
    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)}


def create_submission(app: dict) -> dict:
    validation = validate_submission(app)
    if not validation["valid"]:
        return {"status": "rejected", "validation": validation}
    return {
        "status": "pending_review",
        "app_name": html.escape(app["name"]),
        "category": app["category"],
        "developer": html.escape(app["developer_name"]),
        "review_steps": ["automated_scan", "security_review", "content_review", "approval"],
        "estimated_days": 3,
    }
