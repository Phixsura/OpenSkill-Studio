"""App report — user-submitted app violation reports."""

import html
import secrets
from datetime import datetime, timezone

REPORT_REASONS = {
    "spam": {"label": "Spam or misleading", "severity": "medium"},
    "malware": {"label": "Malware or harmful code", "severity": "critical"},
    "privacy": {"label": "Privacy violation", "severity": "high"},
    "copyright": {"label": "Copyright infringement", "severity": "high"},
    "abuse": {"label": "Abusive content", "severity": "medium"},
    "broken": {"label": "Broken or non-functional", "severity": "low"},
    "other": {"label": "Other", "severity": "low"},
}


def create_report(*, app_id: str, reporter_id: str, reason: str,
                    details: str = "") -> dict:
    reason_info = REPORT_REASONS.get(reason)
    if not reason_info:
        return {"error": f"Invalid reason. Must be: {', '.join(REPORT_REASONS.keys())}"}
    return {
        "report_id": f"rpt_{secrets.token_hex(6)}",
        "app_id": app_id, "reporter_id": reporter_id,
        "reason": reason, "reason_label": reason_info["label"],
        "severity": reason_info["severity"],
        "details": html.escape(details[:1000]),
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_report_queue(*, reports: list[dict]) -> dict:
    open_reports = [r for r in reports if r.get("status") == "open"]
    by_severity: dict[str, int] = {}
    for r in open_reports:
        s = r.get("severity", "low")
        by_severity[s] = by_severity.get(s, 0) + 1
    return {"open": len(open_reports), "total": len(reports),
            "by_severity": by_severity,
            "has_critical": by_severity.get("critical", 0) > 0}
