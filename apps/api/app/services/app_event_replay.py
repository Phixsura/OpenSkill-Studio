"""Event replay service — re-deliver past events for debugging.

Allows developers to replay events that failed delivery or
to test their webhook endpoints with real event data.
"""

import structlog
from datetime import UTC, datetime

log = structlog.get_logger()


def create_replay_request(
    *,
    event_id: str,
    event_type: str,
    original_data: dict,
    target_url: str,
    installation_id: str,
) -> dict:
    """Create an event replay request."""
    return {
        "replay_id": f"replay_{event_id}_{int(datetime.now(UTC).timestamp())}",
        "original_event_id": event_id,
        "event_type": event_type,
        "data": original_data,
        "target_url": target_url,
        "installation_id": installation_id,
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
    }


def validate_replay_request(
    *,
    event_type: str,
    target_url: str,
    max_replays_per_hour: int = 10,
    current_replays_this_hour: int = 0,
) -> dict:
    """Validate whether a replay should be allowed.
    
    Returns {"allowed": bool, "errors": [...]}
    """
    errors = []

    if not event_type:
        errors.append("Event type is required")

    if not target_url:
        errors.append("Target URL is required")
    elif not target_url.startswith(("http://", "https://")):
        errors.append("Target URL must be HTTP(S)")

    if current_replays_this_hour >= max_replays_per_hour:
        errors.append(f"Replay rate limit exceeded ({max_replays_per_hour}/hour)")

    return {"allowed": len(errors) == 0, "errors": errors}
