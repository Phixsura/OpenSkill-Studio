"""App error tracker — collect and analyze sandbox execution errors.

Tracks error patterns, frequencies, and provides error grouping
for developer debugging in the observability dashboard.
"""

from collections import defaultdict
from datetime import UTC, datetime

_error_store: dict[str, list[dict]] = defaultdict(list)


def record_error(
    *,
    app_id: str,
    error_type: str,
    message: str,
    function_name: str | None = None,
    stack_trace: str | None = None,
) -> dict:
    """Record an execution error."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "error_type": error_type,
        "message": message,
        "function_name": function_name,
        "stack_trace": stack_trace,
    }
    _error_store[app_id].append(entry)
    return entry


def get_errors(app_id: str, *, limit: int = 50) -> list[dict]:
    """Get recent errors for an app."""
    return _error_store.get(app_id, [])[-limit:]


def get_error_summary(app_id: str) -> dict:
    """Get error summary grouped by type."""
    errors = _error_store.get(app_id, [])
    by_type: dict[str, int] = defaultdict(int)
    for e in errors:
        by_type[e["error_type"]] += 1
    return {
        "total": len(errors),
        "by_type": dict(by_type),
        "unique_types": len(by_type),
    }


def get_top_errors(app_id: str, *, limit: int = 5) -> list[dict]:
    """Get most frequent error types."""
    summary = get_error_summary(app_id)
    sorted_types = sorted(summary["by_type"].items(), key=lambda x: x[1], reverse=True)
    return [{"error_type": t, "count": c} for t, c in sorted_types[:limit]]


def clear_errors(app_id: str) -> int:
    """Clear error history for an app."""
    count = len(_error_store.pop(app_id, []))
    return count
