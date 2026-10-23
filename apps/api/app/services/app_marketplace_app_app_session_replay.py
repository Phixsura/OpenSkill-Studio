"""Session replay — user session recording metadata."""

import html
import secrets
from datetime import datetime, timezone


def create_session_record(*, user_id: str, page_url: str, duration_s: int,
                            events: int, errors: int = 0) -> dict:
    session_id = f"ses_{secrets.token_hex(8)}"
    return {
        "session_id": session_id, "user_id": user_id,
        "page_url": html.escape(page_url), "duration_s": duration_s,
        "duration_display": f"{duration_s // 60}m {duration_s % 60}s",
        "events": events, "errors": errors,
        "has_errors": errors > 0,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


def build_session_list(*, sessions: list[dict]) -> dict:
    total_duration = sum(s.get("duration_s", 0) for s in sessions)
    error_sessions = sum(1 for s in sessions if s.get("has_errors"))
    return {"sessions": sessions[:20], "total": len(sessions),
            "total_duration_s": total_duration,
            "avg_duration_s": round(total_duration / max(len(sessions), 1)),
            "error_sessions": error_sessions}
