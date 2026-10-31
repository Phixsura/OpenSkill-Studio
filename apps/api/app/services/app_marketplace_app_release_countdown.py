"""Release countdown — countdown timer for upcoming app releases."""

from datetime import datetime, timedelta


def create_countdown(*, app_name: str, version: str, release_date: str,
                       features: list[str]) -> dict:
    try:
        target = datetime.fromisoformat(release_date)
    except ValueError:
        return {"error": "Invalid date format"}
    now = datetime.utcnow()
    delta = target - now
    days = max(delta.days, 0)
    hours = max(delta.seconds // 3600, 0) if delta.total_seconds() > 0 else 0
    return {
        "app_name": app_name,
        "version": version,
        "release_date": release_date,
        "days_remaining": days,
        "hours_remaining": hours,
        "is_released": delta.total_seconds() <= 0,
        "features_preview": features[:5],
        "feature_count": len(features),
    }
