"""Sandbox timeout handler — manage execution timeouts gracefully."""

from datetime import UTC, datetime, timedelta


def check_timeout(started_at: str, timeout_seconds: int) -> dict:
    """Check if an execution has timed out."""
    start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    deadline = start + timedelta(seconds=timeout_seconds)
    now = datetime.now(UTC)
    remaining = (deadline - now).total_seconds()
    return {
        "timed_out": remaining <= 0,
        "remaining_seconds": max(0, round(remaining, 1)),
        "elapsed_seconds": round((now - start).total_seconds(), 1),
        "deadline": deadline.isoformat(),
    }


def format_timeout_error(*, function_name: str, timeout_seconds: int, elapsed_seconds: float) -> dict:
    return {
        "error_type": "TimeoutError",
        "message": f"Function '{function_name}' exceeded {timeout_seconds}s timeout (ran for {elapsed_seconds}s)",
        "function_name": function_name,
        "timeout_seconds": timeout_seconds,
        "elapsed_seconds": elapsed_seconds,
    }
