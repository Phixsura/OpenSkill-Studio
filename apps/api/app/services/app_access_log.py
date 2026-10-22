"""App API access log — track API key usage."""

from collections import defaultdict
from datetime import UTC, datetime

_log: dict[str, list[dict]] = defaultdict(list)


def log_access(*, key_id: str, method: str, path: str, status: int) -> None:
    _log[key_id].append({
        "method": method, "path": path, "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
    })


def get_access_log(key_id: str, *, limit: int = 50) -> list[dict]:
    return _log.get(key_id, [])[-limit:]


def get_access_stats(key_id: str) -> dict:
    entries = _log.get(key_id, [])
    return {
        "total_requests": len(entries),
        "success": sum(1 for e in entries if 200 <= e["status"] < 400),
        "errors": sum(1 for e in entries if e["status"] >= 400),
    }
