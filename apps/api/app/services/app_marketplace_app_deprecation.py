"""App deprecation — schedule sunset, notify users, suggest alternatives."""

from datetime import datetime, timezone


def create_deprecation_notice(*, app: dict, sunset_date: str, reason: str,
                                 alternative_app_id: str | None = None) -> dict:
    return {
        "app_id": app["id"], "app_name": app["name"], "sunset_date": sunset_date,
        "reason": reason, "alternative_app_id": alternative_app_id,
        "status": "announced", "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_deprecation_email(*, notice: dict, install_count: int) -> dict:
    subject = f"Important: {notice['app_name']} will be deprecated"
    body_parts = [
        f"{notice['app_name']} will be sunset on {notice['sunset_date']}.",
        f"Reason: {notice['reason']}",
    ]
    if notice.get("alternative_app_id"):
        body_parts.append(f"We recommend switching to app {notice['alternative_app_id']}.")
    return {"subject": subject, "body": "\n".join(body_parts), "recipients": install_count}


def check_deprecation_status(*, sunset_date: str) -> dict:
    try:
        # Parse date string (YYYY-MM-DD or ISO)
        if "T" in sunset_date:
            sunset = datetime.fromisoformat(sunset_date.replace("Z", "+00:00"))
        else:
            sunset = datetime.strptime(sunset_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return {"phase": "unknown", "days_remaining": None}
    now = datetime.now(timezone.utc)
    days = (sunset - now).days
    if days <= 0:
        phase = "sunset"
    elif days <= 30:
        phase = "final_warning"
    elif days <= 90:
        phase = "deprecation"
    else:
        phase = "announced"
    return {"phase": phase, "days_remaining": max(0, days)}
