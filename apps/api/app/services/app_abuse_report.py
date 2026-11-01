"""App abuse report — handle abuse reports for marketplace apps."""

from datetime import UTC, datetime
from collections import defaultdict

_reports: dict[str, list[dict]] = defaultdict(list)
REPORT_REASONS = ["spam", "malware", "phishing", "trademark", "inappropriate", "broken", "other"]


def submit_report(*, app_id: str, reporter_id: str, reason: str, details: str = "") -> dict | None:
    if reason not in REPORT_REASONS:
        return None
    # One report per user per app
    if any(r["reporter_id"] == reporter_id for r in _reports[app_id]):
        return None
    report = {"app_id": app_id, "reporter_id": reporter_id, "reason": reason,
              "details": details, "status": "pending", "created_at": datetime.now(UTC).isoformat()}
    _reports[app_id].append(report)
    return report


def get_reports(app_id: str) -> list[dict]:
    return _reports.get(app_id, [])


def get_report_count(app_id: str) -> int:
    return len(_reports.get(app_id, []))


def should_auto_suspend(app_id: str, *, threshold: int = 5) -> bool:
    return get_report_count(app_id) >= threshold
