"""Data retention policy — manage data lifecycle and GDPR-compliant deletion."""

from datetime import datetime, timezone, timedelta

RETENTION_PRESETS = {
    "minimal": {"logs_days": 7, "analytics_days": 30, "user_data_days": 90},
    "standard": {"logs_days": 30, "analytics_days": 180, "user_data_days": 365},
    "extended": {"logs_days": 90, "analytics_days": 365, "user_data_days": 730},
    "gdpr_compliant": {"logs_days": 30, "analytics_days": 90, "user_data_days": 365},
}


def create_retention_policy(*, app_id: str, preset: str | None = None,
                               custom: dict | None = None) -> dict:
    if preset and preset not in RETENTION_PRESETS:
        return {"error": f"Unknown preset. Use: {', '.join(sorted(RETENTION_PRESETS))}"}
    config = RETENTION_PRESETS.get(preset, {}) if preset else (custom or RETENTION_PRESETS["standard"])
    return {"app_id": app_id, "preset": preset, "config": config, "error": None}


def compute_data_expiry(*, created_at: str, retention_days: int) -> dict:
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        expires = created + timedelta(days=retention_days)
        now = datetime.now(timezone.utc)
        expired = now > expires
        days_remaining = max(0, (expires - now).days)
        return {"expires_at": expires.isoformat(), "expired": expired,
                "days_remaining": days_remaining}
    except (ValueError, TypeError):
        return {"expires_at": None, "expired": False, "days_remaining": None}


def estimate_data_cleanup(*, data_counts: dict, policy: dict) -> dict:
    cleanup = {}
    for data_type, count in data_counts.items():
        retention = policy.get(f"{data_type}_days", 365)
        # Rough estimate: 1/retention of data expires each day
        daily_cleanup = max(1, count // retention)
        cleanup[data_type] = {"total": count, "daily_cleanup": daily_cleanup,
                               "retention_days": retention}
    return cleanup
