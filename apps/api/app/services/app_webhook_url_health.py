"""Webhook URL health — periodic health check for registered webhook URLs."""

import hashlib
from datetime import UTC, datetime

_url_health: dict[str, dict] = {}


def record_check(url: str, *, reachable: bool, status_code: int | None = None, latency_ms: int = 0) -> None:
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    _url_health[url_hash] = {
        "url": url, "reachable": reachable, "status_code": status_code,
        "latency_ms": latency_ms, "checked_at": datetime.now(UTC).isoformat(),
        "healthy": reachable and (status_code is None or 200 <= status_code < 400),
    }


def get_url_health(url: str) -> dict | None:
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    return _url_health.get(url_hash)


def list_unhealthy_urls() -> list[dict]:
    return [v for v in _url_health.values() if not v.get("healthy")]
