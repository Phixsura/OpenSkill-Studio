"""Event replay — replay historical events for debugging and testing."""

import secrets
from datetime import datetime


def create_replay(*, event_ids: list[str], target_endpoint: str,
                    speed: float = 1.0) -> dict:
    if not event_ids:
        return {"error": "No events to replay"}
    if speed < 0.1 or speed > 10:
        return {"error": "Speed must be 0.1x to 10x"}
    return {
        "replay_id": f"rpl_{secrets.token_urlsafe(8)}",
        "event_count": len(event_ids),
        "target_endpoint": target_endpoint,
        "speed": speed,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "estimated_duration_sec": round(len(event_ids) * 0.5 / speed, 1),
    }


def get_replay_progress(*, total: int, delivered: int, failed: int) -> dict:
    remaining = total - delivered - failed
    pct = round(delivered / max(total, 1) * 100, 1)
    return {
        "total": total, "delivered": delivered, "failed": failed,
        "remaining": remaining, "progress_pct": pct,
        "status": "completed" if remaining == 0 else "in_progress",
    }
