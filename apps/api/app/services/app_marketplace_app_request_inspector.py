"""Request inspector — debug tool for inspecting API requests/responses."""

import json
from datetime import datetime, timezone


def capture_request(*, method: str, path: str, headers: dict, body: str | None = None,
                      status_code: int, response_body: str | None = None,
                      duration_ms: int = 0) -> dict:
    return {
        "method": method, "path": path, "headers": {k: v for k, v in headers.items() if k.lower() != "authorization"},
        "body": body[:1000] if body else None,
        "status_code": status_code, "response_preview": (response_body or "")[:500],
        "duration_ms": duration_ms, "captured_at": datetime.now(timezone.utc).isoformat(),
    }


def search_requests(*, requests: list[dict], status_filter: int | None = None,
                       method_filter: str | None = None, path_contains: str | None = None) -> list[dict]:
    result = requests
    if status_filter:
        result = [r for r in result if r.get("status_code") == status_filter]
    if method_filter:
        result = [r for r in result if r.get("method") == method_filter.upper()]
    if path_contains:
        result = [r for r in result if path_contains in r.get("path", "")]
    return result


def compute_request_stats(*, requests: list[dict]) -> dict:
    if not requests:
        return {"total": 0, "avg_duration_ms": 0, "error_rate": 0}
    total = len(requests)
    errors = sum(1 for r in requests if r.get("status_code", 200) >= 400)
    avg_ms = round(sum(r.get("duration_ms", 0) for r in requests) / total)
    return {"total": total, "avg_duration_ms": avg_ms, "error_rate": round(errors / total * 100, 1)}
