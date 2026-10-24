"""Event replay service — re-deliver past events for debugging.

Allows developers to replay events that failed delivery or
to test their webhook endpoints with real event data.
"""

import ipaddress
import socket
import structlog
from datetime import UTC, datetime
from urllib.parse import urlparse

log = structlog.get_logger()


def _is_safe_replay_url(url: str) -> list[str]:
    """Validate URL is safe for replay delivery (SSRF protection)."""
    errors = []
    if not url:
        errors.append("Target URL is required")
        return errors

    try:
        parsed = urlparse(url)
    except Exception:
        errors.append("Invalid URL format")
        return errors

    if parsed.scheme not in ("http", "https"):
        errors.append("Target URL must be HTTP(S)")
        return errors

    host = (parsed.hostname or "").rstrip(".").lower()
    if not host:
        errors.append("Invalid host")
        return errors

    # DNS resolution + private IP check
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        for info in socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
                errors.append("Target URL resolves to a disallowed address")
                return errors
    except socket.gaierror:
        errors.append("Cannot resolve target hostname")

    return errors


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

    # SSRF-safe URL validation
    url_errors = _is_safe_replay_url(target_url)
    errors.extend(url_errors)

    if current_replays_this_hour >= max_replays_per_hour:
        errors.append(f"Replay rate limit exceeded ({max_replays_per_hour}/hour)")

    return {"allowed": len(errors) == 0, "errors": errors}
