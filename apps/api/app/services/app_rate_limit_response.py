"""Rate limit response builder — build standard rate limit HTTP headers and body."""

from datetime import UTC, datetime


def build_rate_limit_response(*, limit: int, remaining: int, reset_seconds: int) -> dict:
    return {
        "headers": {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(datetime.now(UTC).timestamp()) + reset_seconds),
            "Retry-After": str(reset_seconds) if remaining == 0 else None,
        },
        "exceeded": remaining == 0,
        "error_body": {
            "error": {"code": "RATE_LIMITED", "message": f"Rate limit exceeded. Retry after {reset_seconds}s."}
        } if remaining == 0 else None,
    }
