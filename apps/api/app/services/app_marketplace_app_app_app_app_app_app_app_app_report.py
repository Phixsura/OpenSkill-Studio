"""App report — allow users to report problematic apps."""
from __future__ import annotations
import html
import secrets

REPORT_REASONS = [
    {"id": "spam", "label": "Spam or misleading"},
    {"id": "malware", "label": "Malicious behavior"},
    {"id": "privacy", "label": "Privacy violation"},
    {"id": "broken", "label": "App is broken"},
    {"id": "tos", "label": "Terms of Service violation"},
    {"id": "other", "label": "Other"},
]


def create_report(*, app_id: str, reporter_id: str, reason: str,
                    details: str = "") -> dict:
    if reason not in [r["id"] for r in REPORT_REASONS]:
        return {"error": f"Invalid reason: {reason}"}
    report_id = f"rpt_{secrets.token_hex(6)}"
    return {"report_id": report_id, "app_id": app_id, "reporter": reporter_id,
            "reason": reason, "details": html.escape(details[:1000]),
            "status": "submitted"}


def list_reasons() -> list[dict]:
    return REPORT_REASONS
