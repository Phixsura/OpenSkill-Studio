"""Abuse report — handle user-submitted reports about apps or reviews."""

from datetime import datetime, timezone

VALID_REASONS = {"spam", "malware", "misleading", "copyright", "harassment", "other"}


def create_abuse_report(*, reporter_id: str, target_type: str, target_id: str,
                          reason: str, details: str) -> dict:
    if reason not in VALID_REASONS:
        return {"error": f"Invalid reason. Must be one of: {', '.join(sorted(VALID_REASONS))}"}
    if len(details) < 10:
        return {"error": "Please provide more details (min 10 characters)"}
    if target_type not in ("app", "review", "developer"):
        return {"error": "Invalid target type"}
    return {
        "reporter_id": reporter_id, "target_type": target_type, "target_id": target_id,
        "reason": reason, "details": details, "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(), "error": None,
    }


def prioritize_report(*, report: dict, existing_reports: list[dict]) -> str:
    same_target = [r for r in existing_reports if r.get("target_id") == report["target_id"]]
    if report["reason"] in ("malware", "harassment"):
        return "critical"
    if len(same_target) >= 3:
        return "high"
    if len(same_target) >= 1:
        return "medium"
    return "low"


def resolve_report(*, report: dict, action: str, moderator_id: str) -> dict:
    valid_actions = {"dismiss", "warn", "remove_content", "ban_developer"}
    if action not in valid_actions:
        return {"error": f"Invalid action: {action}"}
    return {
        **report, "status": "resolved", "resolution_action": action,
        "resolved_by": moderator_id, "resolved_at": datetime.now(timezone.utc).isoformat(),
    }
