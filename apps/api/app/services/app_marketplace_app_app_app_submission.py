"""App submission — marketplace app review submission flow."""

import html
import secrets
from datetime import datetime, timezone

REVIEW_CHECKLIST = [
    {"id": "manifest", "label": "Valid app manifest", "auto": True},
    {"id": "security", "label": "Security scan passed", "auto": True},
    {"id": "docs", "label": "Documentation provided", "auto": False},
    {"id": "screenshots", "label": "At least 2 screenshots", "auto": True},
    {"id": "privacy", "label": "Privacy policy link", "auto": True},
    {"id": "testing", "label": "Test coverage > 80%", "auto": True},
]


def create_submission(*, app_id: str, version: str, notes: str = "") -> dict:
    return {
        "submission_id": f"sub_{secrets.token_hex(8)}",
        "app_id": app_id, "version": version,
        "notes": html.escape(notes), "status": "pending_review",
        "checklist": REVIEW_CHECKLIST,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "estimated_review_hours": 24,
    }


def evaluate_checklist(*, results: dict[str, bool]) -> dict:
    items = []
    passed = 0
    for check in REVIEW_CHECKLIST:
        is_pass = results.get(check["id"], False)
        if is_pass:
            passed += 1
        items.append({**check, "pass": is_pass})
    all_pass = passed == len(REVIEW_CHECKLIST)
    return {"checks": items, "passed": passed, "total": len(items),
            "ready_for_review": all_pass, "score": round(passed / len(items) * 100)}
