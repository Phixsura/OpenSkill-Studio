"""App deprecation scheduler — manage deprecation timelines.

Handles sunset dates, migration notices, and auto-revocation
for deprecated apps.
"""

from datetime import UTC, datetime, timedelta


def create_deprecation_plan(
    *,
    app_id: str,
    current_version: str,
    replacement_version: str | None = None,
    sunset_days: int = 90,
    migration_guide_url: str | None = None,
) -> dict:
    """Create a deprecation plan for an app version."""
    now = datetime.now(UTC)
    return {
        "app_id": app_id,
        "deprecated_version": current_version,
        "replacement_version": replacement_version,
        "deprecated_at": now.isoformat(),
        "sunset_date": (now + timedelta(days=sunset_days)).isoformat(),
        "sunset_days": sunset_days,
        "migration_guide_url": migration_guide_url,
        "status": "active",
        "days_remaining": sunset_days,
    }


def check_sunset_status(sunset_date_iso: str) -> dict:
    """Check if a deprecation has reached its sunset date."""
    sunset = datetime.fromisoformat(sunset_date_iso.replace("Z", "+00:00"))
    now = datetime.now(UTC)
    remaining = (sunset - now).days

    if remaining <= 0:
        return {"status": "expired", "days_remaining": 0, "action": "revoke"}
    if remaining <= 7:
        return {"status": "imminent", "days_remaining": remaining, "action": "urgent_notice"}
    if remaining <= 30:
        return {"status": "approaching", "days_remaining": remaining, "action": "reminder"}
    return {"status": "active", "days_remaining": remaining, "action": "none"}


def format_deprecation_notice(plan: dict) -> str:
    """Format a human-readable deprecation notice."""
    lines = [f"⚠️ Version {plan['deprecated_version']} is deprecated."]
    if plan.get("replacement_version"):
        lines.append(f"Please upgrade to v{plan['replacement_version']}.")
    lines.append(f"Sunset date: {plan['sunset_date'][:10]} ({plan['sunset_days']} days).")
    if plan.get("migration_guide_url"):
        lines.append(f"Migration guide: {plan['migration_guide_url']}")
    return " ".join(lines)
