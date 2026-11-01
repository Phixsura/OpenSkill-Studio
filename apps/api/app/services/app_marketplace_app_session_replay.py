"""Session replay — record and analyze user sessions for debugging."""

import secrets
from datetime import datetime, timedelta


def create_session_recording(*, app_id: str, user_id: str, page_url: str,
                               events: list[dict]) -> dict:
    duration_ms = sum(e.get("duration_ms", 0) for e in events) if events else 0
    return {
        "recording_id": f"rec_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "user_id": user_id,
        "page_url": page_url,
        "event_count": len(events),
        "duration_ms": duration_ms,
        "duration_formatted": f"{duration_ms // 60000}m {(duration_ms % 60000) // 1000}s",
        "has_errors": any(e.get("type") == "error" for e in events),
        "has_rage_clicks": any(e.get("type") == "rage_click" for e in events),
        "created_at": datetime.utcnow().isoformat(),
    }


def get_session_insights(*, recordings: list[dict]) -> dict:
    total = len(recordings)
    with_errors = sum(1 for r in recordings if r.get("has_errors"))
    with_rage = sum(1 for r in recordings if r.get("has_rage_clicks"))
    avg_duration = round(sum(r.get("duration_ms", 0) for r in recordings) / max(total, 1))
    return {
        "total_recordings": total,
        "with_errors": with_errors,
        "with_rage_clicks": with_rage,
        "error_rate": round(with_errors / max(total, 1) * 100, 1),
        "avg_duration_ms": avg_duration,
        "frustration_score": round((with_errors + with_rage * 2) / max(total, 1) * 100, 1),
    }
